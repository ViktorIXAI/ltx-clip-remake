#!/bin/bash
# Finish pass scene_11: if 3 boost takes failed lipsync — new keyframe (she sings)
# + a2v 5.0 + fresh seeds; park is paused and resumed afterwards.
cd ~/clip_project || exit 1
for i in $(seq 1 200); do
  grep -q "^\[qc\] scene_11 try3" logs/reshoot11.log 2>/dev/null && break
  sleep 30
done
sleep 10
if grep -q "^\[qc\] scene_11 try3: lip_ok=True" logs/reshoot11.log; then
  echo "try3 OK — finish pass not needed"; exit 0
fi
# kill the boost take (duplicates seed 777) and the runner if still alive
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 20
# park is restarted by the reshoot chain — parked during the finish pass
for i in $(seq 1 20); do grep -q "BATCH5_STARTED" logs/reshoot11_chain.log 2>/dev/null && break; sleep 10; done
sleep 20
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 5
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
python scripts/s11_openmouth_key.py
mv renders/scene_11.mp4 renders_v3_badlip_11.mp4 2>/dev/null
RENDER_SEEDS=11,101,2024 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_11 >> logs/reshoot11b.log 2>&1
# resume the park
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && mkdir -p renders_v1_skin && for i in 01 02 03 04 05 06 07 08 09 10; do mv renders/scene_$i.mp4 renders_v1_skin/ 2>/dev/null; done && python scripts/render_scenes_qc.py scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10 && python scripts/finish_movie.py' >> logs/render_batch5b.log 2>&1 &
echo PARK_RESUMED
