#!/bin/bash
# reshoot22.sh — after PART_P5 (clip 01..25 already delivered) re-shoot scene_22 with the best seed 333.
cd ~/clip_project || exit 1
for i in $(seq 1 600); do
  grep -q "PART_P5_READY" logs/partN.log 2>/dev/null && break
  sleep 30
done
grep -q "PART_P5_READY" logs/partN.log || exit 1
sleep 60
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 15
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
mv renders/scene_22.mp4 renders_v6_weaklip_22.mp4 2>/dev/null
rm -f renders/scene_22.matted
RENDER_SEEDS=333 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_22 >> logs/fix22b.log 2>&1
echo S22_RESHOOT_DONE >> logs/fix22b.log
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && python scripts/finish_movie.py' >> logs/render_batch7.log 2>&1 &
echo PARK7_RESUMED >> logs/fix22b.log
bash scripts/segAB.sh 15 25 1525c >> logs/seg1525c.log 2>&1
echo RESHOOT22_DONE >> logs/fix22b.log
