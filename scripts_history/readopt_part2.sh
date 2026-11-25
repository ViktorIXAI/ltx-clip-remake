#!/bin/bash
# Waits for acceptance of scene_11, re-reviews takes under the fixed lip-sync gate,
# restarts the runner with the new qc_module version, assembles PART2.
cd ~/clip_project || exit 1
while [ ! -s renders/scene_11.mp4 ]; do sleep 30; done
sleep 10
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
python scripts/re_adopt.py scene_11
# softly stop the current runner (it holds the old gate in memory)
ps -ax -o pid,command | grep "[r]ender_scenes_qc.py" | awk '{print $1}' | xargs kill 2>/dev/null
sleep 5
nohup bash -c 'source .venv/bin/activate && export PATH=/opt/homebrew/bin:$PATH && python scripts/render_scenes_qc.py && mkdir -p renders_v1_skin && for i in 01 02 03 04 05 06 07 08 09 10; do mv renders/scene_$i.mp4 renders_v1_skin/ 2>/dev/null; done && python scripts/render_scenes_qc.py scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10 && python scripts/finish_movie.py' >> logs/render_batch4.log 2>&1 &
# PART2 assembly: 01-11 with audio, exact frame math
for i in $(seq 1 11); do printf "file 'renders/scene_%02d.mp4'\n" $i; done > concat_part2.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i concat_part2.txt -c copy preview/_v2.mp4
python3 - <<'EOF'
import json, subprocess
m = json.load(open("manifest.json"))
tf = sum(s["num_frames"] for s in m[:11]); t10 = sum(s["num_frames"] for s in m[:10])
print("SCENE11_START_SEC:", t10/24.0, "TOTAL_SEC:", tf/24.0)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","preview/_v2.mp4","-i","audio/full_mix.wav",
                "-map","0:v","-map","1:a","-t",str(tf/24.0),"-c:v","copy","-c:a","aac","-b:a","320k","preview/PART2.mp4"], check=True)
EOF
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 preview/PART2.mp4
ls -lh preview/PART2.mp4
echo PART2_READY
