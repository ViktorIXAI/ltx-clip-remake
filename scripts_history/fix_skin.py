import json
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
import qc_module  # noqa
import cv2
import numpy as np

OLD_STYLE = "natural soft satin skin texture, subtle cinematic sunset rim light, matte-satin editorial makeup, realistic fine skin details"
NEW_STYLE = "velvet-matte powder-soft skin with zero shine on nose cheeks and forehead, soft satin finish, subtle cinematic sunset rim light, matte-satin editorial makeup, realistic fine skin details"
OLD_NEG = "greasy skin, sweaty face, oily highlights, plastic skin"
NEW_NEG = "greasy skin, sweaty face, oily highlights, shiny glossy skin, wet-look skin, sweat droplets, specular highlights on face, glossy nose, plastic skin"

m = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
for s in m:
    s["prompt"] = s["prompt"].replace(OLD_STYLE, NEW_STYLE)
    s["negative_prompt"] = s["negative_prompt"].replace(OLD_NEG, NEW_NEG)
Path("manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
print("manifest patched:", sum(1 for s in m if NEW_STYLE in s["prompt"]), "prompts,",
      sum(1 for s in m if NEW_NEG in s["negative_prompt"]), "negatives")

n = 0
for s in m:
    p = Path(s["keyframe_image"])
    if not p.exists():
        continue
    img = cv2.imread(str(p))
    if img is None:
        continue
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)
    mask = cv2.GaussianBlur(np.clip((L - 172.0) / 55.0, 0.0, 1.0), (15, 15), 0)
    L2 = np.clip(L - mask * 42.0, 0, 255)
    res = cv2.cvtColor(cv2.merge([L2, A, B]).astype(np.uint8), cv2.COLOR_LAB2BGR)
    res = cv2.bilateralFilter(res, d=5, sigmaColor=32, sigmaSpace=28)
    cv2.imwrite(str(p), res)
    n += 1
print("keyframes re-cleaned:", n)
