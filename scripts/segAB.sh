#!/bin/bash
# segAB.sh <A> <B> <TAG> — cut scenes A..B with audio full_mix.
# If scene B is not yet accepted — takes the freshest tmp take and mats it.
cd ~/clip_project || exit 1
export PATH=/opt/homebrew/bin:$PATH
source .venv/bin/activate
A=$1; B=$2; TAG=$3
printf -v A2 %02d $A; printf -v B2 %02d $B
USE_B=$PWD/renders/scene_$B2.mp4
if [ ! -f renders/scene_$B2.matted ]; then
  NEWB=$(ls -t renders/tmp_scene_${B2}_try*.mp4 2>/dev/null | head -1)
  [ -s "$NEWB" ] || { echo "NO_FILES scene_$B2"; exit 1; }
  echo "USE_TMP=$NEWB"
  python scripts/matte_video.py "$NEWB" /tmp/s${B2}m.mp4 >> logs/seg_$TAG.log 2>&1 || exit 1
  USE_B=/tmp/s${B2}m.mp4
fi
python3 - <<PYEOF > /tmp/seg_$TAG.txt
import json
m = json.load(open("manifest.json"))
d = {s["scene_id"]: s for s in m}
a, b = d["scene_$A2"], d["scene_$B2"]
st = a["start_sec"]; fr = sum(s["num_frames"] for s in m[$((A-1)):$B])
print(round(st, 6), round(fr/24.0, 6), fr)
PYEOF
read ST T FR < /tmp/seg_$TAG.txt
echo "ST=$ST T=$T FR=$FR"
rm -f /tmp/cl_$TAG.txt
for i in $(seq $A $((B-1))); do echo "file '$PWD/renders/scene_$(printf %02d $i).mp4'" >> /tmp/cl_$TAG.txt; done
echo "file '$USE_B'" >> /tmp/cl_$TAG.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/cl_$TAG.txt -c copy /tmp/nosnd_$TAG.mp4
ffmpeg -y -loglevel error -i /tmp/nosnd_$TAG.mp4 -ss $ST -i audio/full_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -t $T preview/SEG_$TAG.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 preview/SEG_$TAG.mp4
echo "SEG_${TAG}_READY"
