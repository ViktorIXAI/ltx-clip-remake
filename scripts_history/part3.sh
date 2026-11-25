#!/bin/bash
# New cut (PART3): all accepted scenes 01-12 as-is + fresh matted 11th,
# with the original audio. Waits for: matted 11th (after boost re-shoot) + accepted 12th.
cd ~/clip_project || exit 1
for i in $(seq 1 240); do
  [ -f renders/scene_11.matted ] && [ -s renders/scene_12.mp4 ] && break
  sleep 30
done
sleep 15
source .venv/bin/activate
export PATH=/opt/homebrew/bin:$PATH
# 12th accepted by old code — mat (idempotent)
python3 -c "
import sys; sys.path.insert(0,'scripts')
import matte_video; matte_video.matte_inplace('renders/scene_12.mp4')"
for i in $(seq 1 12); do printf "file 'renders/scene_%02d.mp4'\n" $i; done > concat_part3.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i concat_part3.txt -c copy preview/_v3.mp4
python3 - <<'EOF'
import json, subprocess
m = json.load(open("manifest.json"))
tf12 = sum(s["num_frames"] for s in m[:12])
t10 = sum(s["num_frames"] for s in m[:10])
t11 = sum(s["num_frames"] for s in m[:11])
mat = sum(s["num_frames"] for s in m[10:12])
print("MATTE_START_SEC:", t10/24.0, "MATTE_SEC:", mat/24.0, "TOTAL_SEC:", tf12/24.0)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","preview/_v3.mp4","-i","audio/full_mix.wav",
                "-map","0:v","-map","1:a","-t",str(tf12/24.0),"-c:v","copy","-c:a","aac","-b:a","320k","preview/PART3.mp4"], check=True)
EOF
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 preview/PART3.mp4
ls -lh preview/PART3.mp4
echo PART3_READY
