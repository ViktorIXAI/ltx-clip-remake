#!/bin/bash
cd ~/clip_project || exit 1
source .venv/bin/activate; export PATH=/opt/homebrew/bin:$PATH
RENDER_SEEDS=2024,11,101 A2V_GUIDANCE=5.0 python scripts/render_scenes_qc.py scene_11 >> logs/fixreal11c.log 2>&1
echo S11c_DONE >> logs/fixreal.log
nohup bash -c "source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && mkdir -p renders_v1_skin && for i in 01 02 03 04 05 06 07 08 09 10; do mv renders/scene_$i.mp4 renders_v1_skin/ 2>/dev/null; done && python scripts/render_scenes_qc.py scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10 && python scripts/finish_movie.py" >> logs/render_batch5c.log 2>&1 &
bash scripts/part3.sh >> logs/part3c.log 2>&1
echo FIXREAL2_DONE >> logs/fixreal.log
