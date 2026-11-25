#!/bin/bash
# Photorealism return: v4 prompts (living skin) + soft matte v3.
cd ~/clip_project || exit 1
for p in $(ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}'); do kill $p 2>/dev/null; done
sleep 15
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
# scene_12: take the raw take and re-matte with the soft matte
if [ -f renders/tmp_scene_12_try1.mp4 ]; then
  cp -f renders/tmp_scene_12_try1.mp4 renders/scene_12.mp4
  rm -f renders/scene_12.matted
  python scripts/matte_video.py renders/scene_12.mp4 renders/scene_12_new.mp4 >> logs/fixreal.log 2>&1
  mv -f renders/scene_12_new.mp4 renders/scene_12.mp4
  touch renders/scene_12.matted
  echo "S12_REMATTE_OK" >> logs/fixreal.log
fi
# scene_11: re-shoot with v4 (seeds: 2024 gave lipsync, +11/101)
mv renders/scene_11.mp4 renders_v4_waxy_11.mp4 2>/dev/null
rm -f renders/scene_11.matted
RENDER_SEEDS=2024,11,101 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_11 >> logs/fixreal11.log 2>&1
echo "S11_DONE" >> logs/fixreal.log
# park continues
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && mkdir -p renders_v1_skin && for i in 01 02 03 04 05 06 07 08 09 10; do mv renders/scene_$i.mp4 renders_v1_skin/ 2>/dev/null; done && python scripts/render_scenes_qc.py scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10 && python scripts/finish_movie.py' >> logs/render_batch5c.log 2>&1 &
echo "PARK_RESUMED" >> logs/fixreal.log
bash scripts/part3.sh >> logs/part3c.log 2>&1
echo "FIXREAL_DONE" >> logs/fixreal.log
