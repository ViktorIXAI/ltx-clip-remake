#!/bin/bash
# Waits for acceptance of scene_12, restarts the runner with the new version (self-heal boost),
# re-shoots scene_11 with stronger audio conditioning, updates PART2, resumes the park.
cd ~/clip_project || exit 1
for i in $(seq 1 100); do
  grep -q "^\[accept\] scene_12" logs/render_batch4.log 2>/dev/null && break
  sleep 30
done
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}' | xargs kill 2>/dev/null
sleep 3
mv renders/scene_11.mp4 renders_v2_badlip_11.mp4 2>/dev/null
RENDER_SEEDS=777,24601,5150 A2V_GUIDANCE=3.0 python scripts/render_scenes_qc.py scene_11 > logs/reshoot11.log 2>&1
# if the new 11th passed lipsync — rebuild PART2
if grep -q "^\[qc\] scene_11 .*lip_ok=True" logs/reshoot11.log || grep -q "^\[accept\] scene_11 .*lip_ok=True" logs/reshoot11.log; then
  for i in $(seq 1 11); do printf "file 'renders/scene_%02d.mp4'\n" $i; done > concat_part2.txt
  ffmpeg -y -loglevel error -f concat -safe 0 -i concat_part2.txt -c copy preview/_v2.mp4
  python3 - <<'EOF'
import json, subprocess
m = json.load(open("manifest.json")); tf = sum(s["num_frames"] for s in m[:11])
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","preview/_v2.mp4","-i","audio/full_mix.wav",
                "-map","0:v","-map","1:a","-t",str(tf/24.0),"-c:v","copy","-c:a","aac","-b:a","320k","preview/PART2.mp4"], check=True)
EOF
  echo "PART2_V2_READY"
else
  echo "PART2_KEPT_V1 (scene 11 lipsync failed again)"
fi
# park continues with new code (self-heal boost for future lipsync failures)
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && mkdir -p renders_v1_skin && for i in 01 02 03 04 05 06 07 08 09 10; do mv renders/scene_$i.mp4 renders_v1_skin/ 2>/dev/null; done && python scripts/render_scenes_qc.py scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10 && python scripts/finish_movie.py' >> logs/render_batch5.log 2>&1 &
echo BATCH5_STARTED
