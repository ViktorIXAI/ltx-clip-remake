#!/usr/bin/env python3
import json
from pathlib import Path
m = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
OLD_STYLE = "velvet-matte powder-soft skin with zero shine on nose cheeks and forehead, soft satin finish, subtle cinematic sunset rim light, matte-satin editorial makeup, realistic fine skin details"
NEW_STYLE = "velvet-matte powder-soft skin with zero shine anywhere on face neck or chest, dry matte cinematic lighting, no rim light sheen on skin, matte editorial makeup, realistic fine skin details"
n = 0
for s in m:
    if OLD_STYLE in s["prompt"]:
        s["prompt"] = s["prompt"].replace(OLD_STYLE, NEW_STYLE); n += 1
    if "shiny glossy skin" not in s["negative_prompt"]:
        s["negative_prompt"] += ", shiny glossy skin, wet-look skin, oily sheen, sweat"
Path("manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"style v3 patched: {n}")
