#!/usr/bin/env python3
"""Render 32 scenes with QC loop and automatic re-shoots (spec v2).
Per scene: up to 3 takes (seed 42, 1337, 9001). Takes go to renders/tmp_{sid}_try{N}.mp4,
check verify_lip_sync (only lip_sync:true) + verify_visual_quality.
renders/{sid}.mp4 gets the best take; early exit when lip_ok and score>=8.
Score log: logs/qc_report.json"""
import json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, "scripts")
import qc_module as qc

M = "models/ltx-2.5"
TRANSFORMER = f"{M}/diffusion_models/ltx-2.5-22b-dev-transformer-bf16.safetensors"
TEXT_ENC = f"{M}/text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors"
LORA = f"{M}/loras/ltx-2.5-22b-distilled-lora-450-bf16.safetensors"
VIDEO_VAE = f"{M}/vae/ltx-2.5-video-vae-bf16.safetensors"
AUDIO_VAE = f"{M}/vae/ltx-2.5-audio-vae-bf16.safetensors"
UPSC = f"{M}/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors"
import os
SEEDS = os.environ.get("RENDER_SEEDS", "42,1337,9001").split(",")
MAX_RETRIES = 3

def render_args(scene, out_path, seed):
    mod = "ltx_pipelines.a2vid_two_stage" if scene["lip_sync"] else "ltx_pipelines.ti2vid_two_stages"
    args = [sys.executable, "-m", mod,
            "--transformer-path", TRANSFORMER, "--text-encoder-path", TEXT_ENC,
            "--video-vae-path", VIDEO_VAE, "--audio-vae-path", AUDIO_VAE,
            "--distilled-lora", LORA, "--spatial-upsampler-path", UPSC,
            "--height", "768", "--width", "1344",
            "--frame-rate", "24", "--num-frames", str(scene["num_frames"]),
            "--image", scene["keyframe_image"], "0", "1.0", "replace",
            "--prompt", scene["prompt"],
            "--negative-prompt", scene["negative_prompt"],
            "--seed", seed, "--output-path", out_path]
    if scene["lip_sync"]:
        args += ["--audio-path", scene["vocals_audio"]]
        boost = os.environ.get("A2V_GUIDANCE")
        if scene.get("a2v_boost") or boost:
            args += ["--a2v-guidance-scale", str(scene.get("a2v_boost", boost))]
    return args

def main():
    only = set(sys.argv[1:]) or None
    manifest = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
    report_path = Path("logs/qc_report.json")
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    for scene in manifest:
        sid = scene["scene_id"]
        if only and sid not in only:
            continue
        final = Path(f"renders/{sid}.mp4")
        if final.exists() and final.stat().st_size > 300_000:
            print(f"[skip] {sid} already accepted", flush=True); continue
        attempts = []
        best = None  # (combined, record)
        for attempt, seed in enumerate(SEEDS[:MAX_RETRIES], 1):
            tmp = f"renders/tmp_{sid}_try{attempt}.mp4"
            t0 = time.time()
            print(f"[render] {sid} attempt {attempt} seed={seed}", flush=True)
            r = subprocess.run(render_args(scene, tmp, seed), capture_output=True, text=True)
            dt = (time.time() - t0) / 60
            if r.returncode != 0 or not Path(tmp).exists():
                print(f"[FAIL-render] {sid} try{attempt} rc={r.returncode} {dt:.1f}min", flush=True)
                Path(f"logs/{sid}_try{attempt}_stderr.log").write_text(r.stderr, encoding="utf-8")
                continue
            lip_ok, corr = (True, None)
            if scene["lip_sync"]:
                lip_ok, corr = qc.verify_lip_sync(tmp, scene["vocals_audio"])
            v_ok, score, why = qc.verify_visual_quality(tmp, scene["prompt"])
            rec = {"scene": sid, "attempt": attempt, "seed": seed, "minutes": round(dt, 1),
                   "lip_ok": bool(lip_ok), "lip_corr": round(float(corr), 3) if corr is not None else None,
                   "visual_ok": bool(v_ok), "score": int(score), "vlm_note": why[:300]}
            attempts.append(rec)
            print(f"[qc] {sid} try{attempt}: lip_ok={lip_ok} corr={corr if corr is None else round(corr,3)} "
                  f"score={score}/10 ({dt:.1f}min)", flush=True)
            combined = score + (3 if lip_ok and scene["lip_sync"] else 0)
            if best is None or combined > best[0]:
                best = (combined, rec, tmp)
            if lip_ok and v_ok:
                break  # early exit: take accepted
        # self-heal: all takes failed lipsync -> bonus take with stronger audio conditioning
        if scene["lip_sync"] and best is not None and not best[1]["lip_ok"]:
            seed = "777"
            tmp = f"renders/tmp_{sid}_tryboost.mp4"
            t0 = time.time()
            print(f"[render] {sid} BOOST take a2v=3.0 seed={seed}", flush=True)
            env = dict(os.environ, A2V_GUIDANCE="3.0")
            r = subprocess.run(render_args(scene, tmp, seed), capture_output=True, text=True, env=env)
            dt = (time.time() - t0) / 60
            if r.returncode == 0 and Path(tmp).exists():
                lip_ok, corr = qc.verify_lip_sync(tmp, scene["vocals_audio"])
                v_ok, score, why = qc.verify_visual_quality(tmp, scene["prompt"])
                rec = {"scene": sid, "attempt": "boost", "seed": seed, "minutes": round(dt, 1),
                       "lip_ok": bool(lip_ok), "lip_corr": round(float(corr), 3) if corr is not None else None,
                       "visual_ok": bool(v_ok), "score": int(score), "vlm_note": why[:300]}
                attempts.append(rec)
                print(f"[qc] {sid} boost: lip_ok={lip_ok} corr={round(corr,3)} score={score}/10 ({dt:.1f}min)", flush=True)
                combined = score + (3 if lip_ok else 0)
                if best is None or combined > best[0]:
                    best = (combined, rec, tmp)
        if best:
            _, rec, tmp = best
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp,
                            "-an", "-c:v", "copy", f"renders/{sid}.mp4"])
            import matte_video
            matte_video.matte_inplace(f"renders/{sid}.mp4")
            print(f"[accept] {sid} <- {tmp} (score={rec['score']}, lip_ok={rec['lip_ok']})", flush=True)
        for p in Path("renders").glob(f"tmp_{sid}_try*.mp4"):
            p.unlink(missing_ok=True)
        report[sid] = attempts
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    accepted = sum(1 for p in Path("renders").glob("scene_*.mp4"))
    print(f"[batch] scenes accepted: {accepted}/32", flush=True)

if __name__ == "__main__":
    main()
