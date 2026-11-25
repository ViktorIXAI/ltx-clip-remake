#!/usr/bin/env python3
"""QC module for clip production (user spec, version 2).
1) select_best_keyframe — smart keyframe selection (sharpness, face geometry, VLM pick, de-gloss)
2) verify_lip_sync — MediaPipe Mouth Aspect Ratio vs RMS envelope of vocals.wav
3) verify_visual_quality — VLM critic (Qwen2.5-VL via MLX) against an artifact checklist"""
import json
import re
from pathlib import Path

import cv2
import librosa
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision
import numpy as np
from scipy.stats import pearsonr

from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

_MODEL_ASSET = str(Path(__file__).resolve().parent.parent / "models/face_landmarker.task")
_landmarker = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mp_tasks.BaseOptions(model_asset_path=_MODEL_ASSET),
    running_mode=vision.RunningMode.IMAGE,
    num_faces=2,
))


def face_landmarks(frame_bgr: np.ndarray):
    """Returns a list of faces; each is 478 NormalizedLandmarks (MediaPipe Face Mesh indices)."""
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    res = _landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    return res.face_landmarks
_vlm_cache = {}


def get_vlm(model_path="models/vlm_critic"):
    if "model" not in _vlm_cache:
        model, processor = load(model_path)
        config = load_config(model_path)
        _vlm_cache["model"] = (model, processor, config)
    return _vlm_cache["model"]


def ask_vlm(image_paths: list[str], prompt: str) -> str:
    model, processor, config = get_vlm()
    formatted = apply_chat_template(processor, config, prompt, num_images=len(image_paths))
    out = generate(model, processor, formatted, image_paths, max_tokens=200, temperature=0.1)
    return out.text if hasattr(out, "text") else str(out)


def clean_skin_glare(img_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)
    mask = cv2.GaussianBlur(np.clip((L - 172.0) / 55.0, 0.0, 1.0), (15, 15), 0)
    L_clean = np.clip(L - mask * 42.0, 0, 255)
    res = cv2.cvtColor(cv2.merge([L_clean, A, B]).astype(np.uint8), cv2.COLOR_LAB2BGR)
    return cv2.bilateralFilter(res, d=5, sigmaColor=32, sigmaSpace=28)


def select_best_keyframe(video_path: str, center_sec: float, out_path: str, scene_desc: str) -> str:
    """Picks the sharpest, best-proportioned frame in a ±1.2 s window and cleans skin."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    candidates = []
    tmp_dir = Path("assets/candidates")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for idx, offset in enumerate(np.linspace(-1.2, 1.2, 9)):
        f_idx = int(np.clip((center_sec + offset) * fps, 0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        frame_16x9 = _crop_16x9(frame)
        gray = cv2.cvtColor(frame_16x9, cv2.COLOR_BGR2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Face proportion check (drops flattened stub frames)
        rgb = cv2.cvtColor(frame_16x9, cv2.COLOR_BGR2RGB)
        faces = face_landmarks(frame_16x9)
        ratio_penalty = 1.0
        if faces:
            lm = faces[0]
            xs = [p.x * 1280 for p in lm]
            ys = [p.y * 720 for p in lm]
            w, h = (max(xs) - min(xs)), (max(ys) - min(ys) + 1e-5)
            aspect = w / h  # Normal for a face ~0.68..0.88; flattened frames give > 1.05
            if aspect > 1.02:
                ratio_penalty = 0.05
        score = sharpness * ratio_penalty
        cand_file = tmp_dir / f"{Path(out_path).stem}_c{idx}.png"
        cv2.imwrite(str(cand_file), frame_16x9)
        candidates.append((score, str(cand_file), frame_16x9))
    cap.release()
    candidates.sort(key=lambda x: x[0], reverse=True)
    top3 = [c[1] for c in candidates[:3]]
    # Final pick of best of top-3 via the vision model
    if len(top3) > 1:
        q = (
            f"Pick the single best keyframe (index 0, 1, or 2) for scene: '{scene_desc}'. "
            "Reject frames with motion blur, closed eyes, squashed/wide distorted faces, or transition fades. "
            'Reply ONLY with JSON: {"best_index": 0}'
        )
        ans = ask_vlm(top3, q)
        m = re.search(r'"best_index"\s*:\s*(\d)', ans)
        chosen_idx = int(m.group(1)) if m and int(m.group(1)) < len(top3) else 0
    else:
        chosen_idx = 0
    best_frame = cv2.imread(top3[chosen_idx])
    cleaned = clean_skin_glare(best_frame)
    cv2.imwrite(out_path, cleaned)
    return out_path


def verify_lip_sync(video_path: str, vocals_wav: str, fps: int = 24) -> tuple[bool, float]:
    """Checks correlation of mouth opening with vocal energy."""
    y, sr = librosa.load(vocals_wav, sr=16000)
    hop = int(sr / fps)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    # Instrumental segment: no vocals — lipsync requirement not applied
    if np.std(rms) < 1e-4 or float(rms.max()) < 0.01:
        return True, None
    # mask of frames with audible vocals (threshold from this window RMS peak)
    vocal_mask = rms >= max(float(rms.max()) * 0.08, 2e-3)
    cap = cv2.VideoCapture(video_path)
    # Separate MAR series per face (frame -> mar) so that
    # the man's silent profile does not break the singing woman's score.
    series = {0: {}, 1: {}}
    fi = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        for j, lm in enumerate(face_landmarks(frame)[:2]):
            # Inner upper/lower lip (13, 14) and mouth corners (78, 308)
            v_dist = abs(lm[14].y - lm[13].y)
            h_dist = abs(lm[308].x - lm[78].x) + 1e-5
            series[j][fi] = v_dist / h_dist
        fi += 1
    cap.release()
    best_corr = -1.0
    for j, smap in series.items():
        if len(smap) < 12:
            continue
        idx = np.array(sorted(smap))
        mar = np.array([smap[i] for i in idx if i < len(rms)])
        r = rms[idx[idx < len(rms)]]
        if len(r) < 12 or np.std(r) < 1e-4 or float(r.max()) < 0.01 or np.std(mar) < 1e-4:
            continue
        c, _ = pearsonr(r, mar)
        best_corr = max(best_corr, float(c))
    # TAIL GATE: on frames without vocals the mouth must not openly 'whisper'.
    # Applied only to scenes with clear vocals (coverage >=60%): quiet singing
    # is indistinguishable from breathing by RMS, and the gate would give false failures.
    whisper_max = 0.0
    nfr = max(max(s2) for s2 in series.values() if s2) + 1 if (series[0] or series[1]) else 0
    coverage = float(vocal_mask[:nfr].mean()) if nfr else 0.0
    if coverage >= 0.60:
        for smap in series.values():
            if not smap:
                continue
            idx_all = np.array(sorted(smap))
            keep = idx_all < len(vocal_mask)
            idx_all = idx_all[keep]
            mar_all = np.array([smap[i] for i in idx_all])
            vmf = vocal_mask[idx_all]
            silent = mar_all[~vmf]
            if len(silent) >= 8:
                whisper_max = max(whisper_max, float(silent.mean()))
    # If audio has active vocals, lip-motion correlation must be >= 0.28
    lip_ok = (best_corr >= 0.28) and (whisper_max <= 0.30)
    return lip_ok, (best_corr if best_corr >= 0.0 else best_corr)


def verify_visual_quality(video_path: str, prompt: str) -> tuple[bool, int, str]:
    """Checks 5 render frames via VLM for skin/hand/teeth/outline artifacts."""
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_paths = []
    tmp_dir = Path("logs/qc_frames")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for idx in np.linspace(2, max(2, total - 3), 5, dtype=int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok:
            p = tmp_dir / f"{Path(video_path).stem}_f{idx}.jpg"
            cv2.imwrite(str(p), frame)
            sample_paths.append(str(p))
    cap.release()
    q = (
        f"You are a strict cinema QC supervisor. Evaluate these 5 frames generated for: '{prompt}'. "
        "Check for: 1) extra/deformed fingers or hands, 2) melted/distorted teeth or mouth, "
        "3) greasy/sweaty oily or glossy shiny skin (faces must be matte and velvet-soft; shine on nose, cheeks or forehead is a fail), 4) unnatural neon outline artifacts, 5) squashed wide faces. "
        'Score from 1 to 10 (pass >= 8). Reply ONLY in JSON: {"score": 8, "reason": "short note"}'
    )
    ans = ask_vlm(sample_paths, q)
    m_score = re.search(r'"score"\s*:\s*(\d+)', ans)
    score = int(m_score.group(1)) if m_score else 7
    return (score >= 8), score, ans


def _crop_16x9(frame: np.ndarray) -> np.ndarray:
    """Center crop to 16:9 (no stretching) then resize 1280x720."""
    h, w = frame.shape[:2]
    if w / h > 16 / 9:
        nh = int(w * 9 / 16)
        y0 = max(0, (h - nh) // 2)
        frame = frame[y0:y0 + nh, :]
    else:
        nw = int(h * 16 / 9)
        x0 = max(0, (w - nw) // 2)
        frame = frame[:, x0:x0 + nw]
    return cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LANCZOS4)
