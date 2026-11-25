#!/bin/bash
cd ~/clip_project
bash scripts/partN.sh 17 P4 >> logs/partN.log 2>&1
bash scripts/partN.sh 25 P5 >> logs/partN.log 2>&1
echo BUILD45_DONE >> logs/partN.log
