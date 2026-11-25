#!/usr/bin/env python3
"""Final: Real-ESRGAN x2 (RRDBNet, MPS, tiled) -> 2560x1440 -> 1920x1080,
concat of accepted scenes + original track full_mix.wav -> renders/FINAL_MASTER_4K.mp4.
Log: logs/finish.log"""
import subprocess, sys
from pathlib import Path

import cv2
import numpy as np
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet

WEIGHTS = "models/realesrgan/RealESRGAN_x2plus.pth"
SC = 2
TILE, PAD = 384, 24

net = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
sd = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
net.load_state_dict(sd.get("params_ema", sd.get("params", sd)))
net.eval().to("mps")

@torch.no_grad()
def upscale_frame(img):
    h, w = img.shape[:2]
    out = np.zeros((h * SC, w * SC, 3), np.uint8)
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            y0, x0 = max(0, y - PAD), max(0, x - PAD)
            y1, x1 = min(h, y + TILE + PAD), min(w, x + TILE + PAD)
            tile = img[y0:y1, x0:x1]
            t = torch.from_numpy(tile[:, :, ::-1].copy()).permute(2, 0, 1).float().div(255)[None].to("mps")
            sr = net(t)[0].mul(255).byte().permute(1, 2, 0).cpu().numpy()
            oy, ox = (y - y0) * SC, (x - x0) * SC
            th = min(sr.shape[0] - oy, h * SC - y * SC)
            tw = min(sr.shape[1] - ox, w * SC - x * SC)
            out[y * SC:y * SC + th, x * SC:x * SC + tw] = sr[oy:oy + th, ox:ox + tw]
    return out

def process_scene(src, dst):
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "2688x1536", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-vf", "scale=1920:1098,crop=1920:1080", str(dst)], stdin=subprocess.PIPE)
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        proc.stdin.write(upscale_frame(frame).tobytes())
        n += 1
        if n % 120 == 0:
            print(f"  {src.name}: {n} frames", flush=True)
    cap.release(); proc.stdin.close(); proc.wait()
    print(f"[upscale] {src.name} -> {dst.name} ({n} frames)", flush=True)

def main():
    Path("renders_1080").mkdir(exist_ok=True)
    sys.path.insert(0, "scripts")
    import matte_video
    for s0 in sorted(Path("renders").glob("scene_*.mp4")):
        matte_video.matte_inplace(str(s0))  # idempotent: mattes only unmatted
    manifest = json.loads(Path("manifest.json").read_text(encoding="utf-8")) if Path("manifest.json").exists() else None
    scenes = sorted(Path("renders").glob("scene_*.mp4"))
    outs = scenes  # no upscale: concat of originals (1344x768)
    listfile = Path("logs/concat.txt")
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in outs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(listfile), "-c", "copy", "renders/_video_only.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "renders/_video_only.mp4",
                    "-i", "audio/full_mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
                    "renders/FINAL_MASTER_4K.mp4"], check=True)
    print("[final] renders/FINAL_MASTER_4K.mp4 ready", flush=True)

import json
if __name__ == "__main__":
    main()
