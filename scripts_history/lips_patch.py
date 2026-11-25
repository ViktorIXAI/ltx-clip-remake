import json
from pathlib import Path

TAIL = ("her mouth articulates the sung lyrics continuously and naturally throughout the shot, "
        "never sealing or closing her lips while vocals are audible, both faces fully visible and unobstructed, "
        "singing to each other")
NEG = "lips fused together, mouth occluded by another face, sealed lips while singing, silent mouth movement"

m = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
n = 0
for s in m:
    if not s["lip_sync"]:
        continue
    if "articulates the sung lyrics" not in s["prompt"]:
        s["prompt"] = s["prompt"].rstrip().rstrip(".") + ". " + TAIL
        n += 1
    if NEG not in s["negative_prompt"]:
        s["negative_prompt"] = s["negative_prompt"] + ", " + NEG
Path("manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
print("lips patched:", n, "lip-sync scenes")
