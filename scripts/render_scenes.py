#!/usr/bin/env python3
"""Batch render of manifest.json scenes via LTX-2.3 (official LTX-2 pipelines).
lip_sync=true  -> A2VidTwoStage (keyframe + vocals-audio conditioning)
lip_sync=false -> TI2VidTwoStages (keyframe + prompt, without audio conditioning)
Every render: renders/scene_XX.mp4. Re-runs skip finished scenes."""
import json, subprocess, sys, time
from pathlib import Path

CKPT = "models/LTX-2.3/ltx-2.3-22b-dev.safetensors"
GEMMA = "models/gemma-3-12b"
LORA = "models/LTX-2.3/ltx-2.3-22b-distilled-lora-384-1.1.safetensors"
UPSC = "models/LTX-2.3/ltx-2.3-spatial-upscaler-x2-1.1.safetensors"
SEED = "42"

def base_args(scene):
    return [
        "--checkpoint-path", CKPT,
        "--gemma-root", GEMMA,
        "--distilled-lora", LORA,
        "--spatial-upsampler-path", UPSC,
        "--height", "720", "--width", "1280",
        "--frame-rate", "24", "--num-frames", str(scene["num_frames"]),
        "--image", scene["keyframe_image"], "0", "1.0", "replace",
        "--prompt", scene["prompt"],
        "--negative-prompt", scene["negative_prompt"],
        "--seed", SEED,
        "--output-path", f"renders/{scene['scene_id']}.mp4",
    ]

def main():
    only = sys.argv[1:] and set(sys.argv[1:]) or None
    manifest = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
    done = fail = 0
    for scene in manifest:
        sid = scene["scene_id"]
        if only and sid not in only:
            continue
        out = Path(f"renders/{sid}.mp4")
        if out.exists() and out.stat().st_size > 300_000:
            print(f"[skip] {sid} already done", flush=True); done += 1; continue
        mod = "ltx_pipelines.a2vid_two_stage" if scene["lip_sync"] else "ltx_pipelines.ti2vid_two_stages"
        args = [sys.executable, "-m", mod] + base_args(scene)
        if scene["lip_sync"]:
            args += ["--audio-path", scene["vocals_audio"]]
        t0 = time.time()
        print(f"[start] {sid} mod={mod} frames={scene['num_frames']}", flush=True)
        r = subprocess.run(args, capture_output=True, text=True)
        dt = (time.time() - t0) / 60
        if r.returncode == 0 and out.exists():
            print(f"[done] {sid} in {dt:.1f} min", flush=True); done += 1
        else:
            print(f"[FAIL] {sid} rc={r.returncode} in {dt:.1f} min\n{r.stderr[-2000:]}", flush=True)
            Path(f"logs/{sid}_stderr.log").write_text(r.stderr, encoding="utf-8")
            fail += 1
    print(f"[batch] done {done}, errors {fail}", flush=True)

if __name__ == "__main__":
    main()
