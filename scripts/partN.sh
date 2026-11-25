#!/bin/bash
# partN.sh <NN> <NAME> — assemble preview 01..NN with audio, without touching the park.
cd ~/clip_project || exit 1
LAST=$1; TAG=$2
export PATH=/opt/homebrew/bin:$PATH
source .venv/bin/activate
# wait for the scene file and its matte (marker appears after acceptance)
for i in $(seq 1 400); do
  [ -s renders/scene_$(printf %02d $LAST).mp4 ] && [ -f renders/scene_$(printf %02d $LAST).matted ] && break
  sleep 30
done
[ -f renders/scene_$(printf %02d $LAST).matted ] || { echo "TIMEOUT_WAIT scene_$LAST"; exit 1; }
# mat fresh unmarked scenes inside the range
for i in $(seq 1 $LAST); do
  f=renders/scene_$(printf %02d $i).mp4
  if [ -s $f ] && [ ! -f $f.matted ]; then
    python scripts/matte_video.py $f $f.matetmp.mp4 >> logs/partN.log 2>&1 && mv $f.matetmp.mp4 $f && touch $f.matted
  fi
done
# exact frame math: sum of manifest num_frames
python3 - <<PYEOF > /tmp/dur_$TAG.txt
import json
m=json.load(open("manifest.json"))
fr=sum(s["num_frames"] for s in m[:$LAST])
print(fr/24.0, fr)
PYEOF
read T FR < /tmp/dur_$TAG.txt
echo "TOTAL_SEC=$T FRAMES=$FR"
rm -f /tmp/cl_$TAG.txt
for i in $(seq 1 $LAST); do echo "file '$PWD/renders/scene_$(printf %02d $i).mp4'" >> /tmp/cl_$TAG.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/cl_$TAG.txt -c copy -t $T /tmp/nosnd_$TAG.mp4
ffmpeg -y -loglevel error -i /tmp/nosnd_$TAG.mp4 -i audio/full_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -t $T preview/PART_$TAG.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 preview/PART_$TAG.mp4
echo "PART_${TAG}_READY"
