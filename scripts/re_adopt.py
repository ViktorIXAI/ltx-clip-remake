#!/usr/bin/env python3
"""Re-reviews all takes of a scene under the fixed lip-sync gate (best of 2 faces)
and swaps the accepted file for the best passing take."""
import sys, shutil, json
from pathlib import Path
sys.path.insert(0, "scripts")
import qc_module

SID = sys.argv[1] if len(sys.argv) > 1 else "scene_11"
manifest = {s["scene_id"]: s for s in json.load(open("manifest.json"))}
scene = manifest[SID]
import glob
voc = glob.glob("audio/stems/*/*/vocals.wav")[0]
import librosa
y, sr = librosa.load(voc, sr=22050, offset=scene["start_sec"], duration=scene["duration_sec"])
tmpw = Path(f"logs/{SID}_voc_slice.wav"); tmpw.parent.mkdir(exist_ok=True)
import soundfile as sf
sf.write(tmpw, y, sr)

cands = sorted(glob.glob(f"renders/tmp_{SID}_try*.mp4")) + [f"renders/{SID}.mp4", f"renders_v1_badlip_{SID.split('_')[1]}.mp4" if SID.startswith("scene_") else ""]
results = []
for c in cands:
    p = Path(c)
    if not p.exists() or p.stat().st_size == 0:
        continue
    ok, corr = qc_module.verify_lip_sync(str(p), str(tmpw))
    print(f"[re-adopt] {c}: lip_ok={ok} corr={corr if corr is None else round(corr,3)}", flush=True)
    results.append((corr, ok, c))

good = [r for r in results if r[1]]
target = Path(f"renders/{SID}.mp4")
if good:
    good.sort(reverse=True)
    best = good[0][2]
    if str(target) != best:
        shutil.copy(best, target)
        print(f"[re-adopt] REPLACED {target} <- {best} (corr={good[0][0] if good[0][0] is None else round(good[0][0],3)})", flush=True)
    else:
        print(f"[re-adopt] current adopted file already best", flush=True)
else:
    best = max(results) if results else None
    print(f"[re-adopt] NO passing takes; best {best}", flush=True)
