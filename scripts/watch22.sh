#!/bin/bash
# Rescue scene_22: if the park accepted it with lip_ok=False — keyframe max-MAR + A2V 5.0.
cd ~/clip_project || exit 1
for i in $(seq 1 400); do
  grep -q "^\[accept\] scene_22 .* lip_ok=False" logs/render_batch6b.log 2>/dev/null && break
  grep -q "^\[accept\] scene_22 .* lip_ok=True" logs/render_batch6b.log 2>/dev/null && exit 0
  sleep 30
done
grep -q "^\[accept\] scene_22 .* lip_ok=False" logs/render_batch6b.log || exit 1
sleep 240   # give the park time to reach scene_23 and start rendering
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 15
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
mv renders/scene_22.mp4 renders_v5_badlip_22.mp4 2>/dev/null
rm -f renders/scene_22.matted
python scripts/s22_openmouth_key.py && RENDER_SEEDS=2024,7,333 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_22 >> logs/fix22.log 2>&1
echo S22_RESCUE_DONE >> logs/fix22.log
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && python scripts/finish_movie.py' >> logs/render_batch6c.log 2>&1 &
echo PARK6C_RESUMED >> logs/fix22.log
bash scripts/partN.sh 25 P5 >> logs/partN.log 2>&1
echo WATCH22_DONE >> logs/fix22.log
