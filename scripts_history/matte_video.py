#!/usr/bin/env python3
"""Matting post-pass: removes specular skin gloss in face regions
(FaceLandmarker zones with dilation), leaving background and garland lights untouched.
Usage: matte_video.py <video.mp4> [test_frame.jpg]"""
import sys, cv2, numpy as np
from pathlib import Path
sys.path.insert(0, "scripts")
from qc_module import face_landmarks

def face_boxes(frame):
    boxes = []
    for lm in face_landmarks(frame)[:2]:
        xs = [p.x for p in lm]; ys = [p.y for p in lm]
        x1, x2 = min(xs), max(xs); y1, y2 = min(ys), max(ys)
        w, h = x2 - x1, y2 - y1
        boxes.append((x1 - 0.15*w, y1 - 0.15*h, x2 + 0.15*w, min(1.0, y2 + 0.85*h)))  # including neck/collarbones
    return boxes

def matte_region(frame, box):
    H, W = frame.shape[:2]
    x1 = max(0, int(box[0]*W)); x2 = min(W, int(box[2]*W))
    y1 = max(0, int(box[1]*H)); y2 = min(H, int(box[3]*H))
    if x2 <= x1 or y2 <= y1:
        return frame
    roi = frame[y1:y2, x1:x2]
    # v3 de-gloss: cut large light blotches (grease) by RGB scaling
    # proportionally (brightness and color together) — no color blotches from LAB separation.
    roi_f = roi.astype(np.float32)
    B_, G_, R_ = cv2.split(roi_f)
    L = 0.114 * B_ + 0.587 * G_ + 0.299 * R_
    hp = L - cv2.GaussianBlur(L, (0, 0), 14)
    L2 = L - np.clip(hp, 0, None) * 0.45
    L2 = L2 + 0.30 * (L2 - cv2.GaussianBlur(L2, (0, 0), 1.2))  # pore micro-contrast
    r = np.clip(L2 / np.maximum(L, 1.0), 0.72, 1.12)
    out = np.dstack([np.clip(c * r, 0, 255) for c in (B_, G_, R_)]).astype(np.uint8)
    # soft blend along eroded border to avoid blotches
    alpha = np.zeros((y2-y1, x2-x1), np.float32)
    cv2.rectangle(alpha, (12, 12), (x2-x1-12, y2-y1-12), 1.0, -1)
    alpha = cv2.GaussianBlur(alpha, (41, 41), 0)[..., None]
    frame[y1:y2, x1:x2] = (out * alpha + roi * (1 - alpha)).astype(np.uint8)
    return frame

def process_video(in_path, out_path):
    cap = cv2.VideoCapture(in_path)
    fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); H = int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (W, H))
    if not vw.isOpened():
        vw = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    n = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        for b in face_boxes(f):
            f = matte_region(f, b)
        vw.write(f); n += 1
        if n % 40 == 0:
            print(f"[matte] {in_path}: {n} frames", flush=True)
    cap.release(); vw.release()
    print(f"[matte] done {out_path} ({n} frames)", flush=True)

def matte_inplace(video_path):
    p = Path(video_path)
    if p.with_suffix('.matted').exists():
        print(f"[matte] {p} already matted", flush=True); return
    tmp = str(p) + ".matetmp.mp4"
    process_video(str(p), tmp)
    import shutil; shutil.move(tmp, str(p))
    p.with_suffix('.matted').write_text('ok')

if __name__ == "__main__":
    src = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2].endswith(".jpg"):
        f = cv2.imread(src)
        # single frame: read frame from video by index
        cap = cv2.VideoCapture(src); cap.read(); f = None; cap.release()
    if src.endswith(".jpg"):
        f = cv2.imread(src)
        for b in face_boxes(f):
            f = matte_region(f, b)
        cv2.imwrite(sys.argv[2], f)
    else:
        process_video(src, sys.argv[2])
