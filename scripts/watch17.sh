#!/bin/bash
# Rescue scene_17: if the park accepted it with lip_ok=False — re-shoot with two-gender tail hint.
cd ~/clip_project || exit 1
for i in $(seq 1 400); do
  grep -q "^\[accept\] scene_17 .* lip_ok=False" logs/render_batch5c.log 2>/dev/null && break
  grep -q "^\[accept\] scene_17 .* lip_ok=True" logs/render_batch5c.log 2>/dev/null && exit 0
  sleep 30
done
grep -q "^\[accept\] scene_17 .* lip_ok=False" logs/render_batch5c.log || exit 1
sleep 240   # give the park time to reach scene_18 and start rendering
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 15
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
mv renders/scene_17.mp4 renders_v5_badwhisper_17.mp4 2>/dev/null
rm -f renders/scene_17.matted
python scripts/s17_openmouth_key.py && RENDER_SEEDS=2024,7,333 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_17 >> logs/fix17.log 2>&1
echo S17_RESCUE_DONE >> logs/fix17.log
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && python scripts/finish_movie.py' >> logs/render_batch6.log 2>&1 &
echo PARK6_RESUMED >> logs/fix17.log
bash scripts/partN.sh 17 P4 >> logs/partN.log 2>&1
bash scripts/partN.sh 25 P5 >> logs/partN.log 2>&1
echo WATCH17_DONE >> logs/fix17.log
