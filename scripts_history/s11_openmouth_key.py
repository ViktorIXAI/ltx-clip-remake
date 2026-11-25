#!/usr/bin/env python3
"""Keyframe scene_11 = source frame with maximum mouth opening
(she is already singing) -> makes it easier for the model to continue singing. backs up the old frame."""
import sys, json, shutil, glob
import cv2, numpy as np
sys.path.insert(0, "scripts")
from qc_module import face_landmarks, clean_skin_glare

m = {s["scene_id"]: s for s in json.load(open("manifest.json"))}
s = m["scene_11"]
cap = cv2.VideoCapture("input/source_clip.mp4")
fps = cap.get(cv2.CAP_PROP_FPS) or 24
f0 = int(s["start_sec"] * fps); f1 = int((s["start_sec"] + s["duration_sec"]) * fps)
cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
best = (-1, None); n = 0
while cap.get(cv2.CAP_PROP_POS_FRAMES) < f1:
    ok, fr = cap.read()
    if not ok: break
    n += 1
    fr = cv2.resize(fr, (1280, 720))
    fs = face_landmarks(fr)
    if fs:
        # max mouth opening among faces: catch the moment she sings
        mar = max(abs(lm[14].y - lm[13].y) / (abs(lm[308].x - lm[78].x) + 1e-5) for lm in fs[:2])
        if mar > best[0]:
            best = (mar, fr.copy())
cap.release()
print("scanned", n, "best MAR", round(best[0], 3))
if best[1] is not None:
    shutil.copy("assets/keyframes_clean/scene_11.png", "assets/keyframes_clean/scene_11.png.bak")
    cv2.imwrite("assets/keyframes_clean/scene_11.png", clean_skin_glare(best[1]))
    print("keyframe replaced (backup .bak)")
