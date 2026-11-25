#!/usr/bin/env python3
"""QC re-selection of keyframes for all scenes from manifest.json (select_best_keyframe)."""
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
import qc_module as qc

manifest = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
for scene in manifest:
    sid = scene["scene_id"]
    out = f"assets/keyframes_clean/{sid}.png"
    center = scene["start_sec"] + scene["duration_sec"] / 2.0
    qc.select_best_keyframe("input/source_clip.mp4", center, out, scene["prompt"][:200])
    print(f"[keyframe] {sid} -> {out}", flush=True)
print("[keyframes] done:", len(manifest))
