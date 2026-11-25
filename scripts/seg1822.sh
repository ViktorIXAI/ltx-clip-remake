#!/bin/bash
# seg1822.sh — preview of scenes 18..22 (fresh rescue take of scene 22) with audio from full_mix.
cd ~/clip_project || exit 1
export PATH=/opt/homebrew/bin:$PATH
source .venv/bin/activate
NEW22=$(ls -t renders/tmp_scene_22_try*.mp4 2>/dev/null | head -1)
echo "NEW22=$NEW22"
python scripts/matte_video.py "$NEW22" /tmp/s22m.mp4 >> logs/seg1822.log 2>&1 || exit 1
python3 - <<'PYEOF' > /tmp/seg1822.txt
import json
m = json.load(open("manifest.json"))
d = {s["scene_id"]: s for s in m}
a, b = d["scene_18"], d["scene_22"]
st = a["start_sec"]; fr = sum(s["num_frames"] for s in m[17:22])
print(round(st, 6), round(fr/24.0, 6), fr)
PYEOF
read ST T FR < /tmp/seg1822.txt
echo "ST=$ST T=$T FR=$FR"
rm -f /tmp/cl_seg.txt
for i in $(seq 18 21); do echo "file '$PWD/renders/scene_$(printf %02d $i).mp4'" >> /tmp/cl_seg.txt; done
echo "file '/tmp/s22m.mp4'" >> /tmp/cl_seg.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/cl_seg.txt -c copy /tmp/nosnd_seg.mp4
ffmpeg -y -loglevel error -i /tmp/nosnd_seg.mp4 -ss $ST -i audio/full_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -t $T preview/SEG1822.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 preview/SEG1822.mp4
echo "SEG1822_READY"
