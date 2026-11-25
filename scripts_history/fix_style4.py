#!/usr/bin/env python3
"""Prompts v4: restore photorealistic skin. v3 overdid it: 'zero shine
anywhere / velvet-matte powder-soft / no rim light' -> plastic. v4: living skin
with pores and natural micro-gloss, only GREASY shine/sweat is banned."""
import json

NEW_STYLE_TAIL = (
    "natural realistic human skin with visible pores and fine micro-texture, "
    "soft diffuse cinematic lighting, healthy low-sheen skin that is neither "
    "oily nor airbrushed, subtle film grain, "
    "shot on 35mm cinema lens, Arri Alexa color science"
)
NEW_NEG = (
    "[STYLE-NEG] oily sheen, greasy skin, sweaty face, sweat droplets, "
    "wet-look skin, shiny glossy skin, plastic waxy mannequin skin, "
    "airbrushed beauty filter, over-smoothed porcelain skin, caked matte makeup, "
    "enlarged pores, "
)

m = json.load(open("manifest.json"))
for s in m:
    p = s["prompt"]
    # cut old style tails: everything from the first gloss marker to the end or to the lips tail
    for marker in ("velvet-matte powder-soft skin", "dry matte cinematic lighting"):
        i = p.find(marker)
        if i != -1:
            j = p.find("shot on 35mm cinema lens, Arri Alexa color science.", i)
            j = j + len("shot on 35mm cinema lens, Arri Alexa color science.") if j != -1 else i
            # keep the lips tail after the style point if attached
            rest = p[j:]
            k = rest.find("her mouth articulates")
            lips = rest[k:] if k != -1 else ""
            p = p[:i] + NEW_STYLE_TAIL + ((", " + lips) if lips else "")
            break
    s["prompt"] = p
    n = s["negative_prompt"]
    i = n.find("[STYLE-NEG")
    if i != -1:
        j = n.find("plastic skin")
        j = j + len("plastic skin") if j != -1 else i
        k = n.find("stretched aspect ratio", j)
        tail = n[k:] if k != -1 else ""
        n = n[:i] + NEW_NEG + tail
        s["negative_prompt"] = n
json.dump(m, open("manifest.json", "w"), indent=1, ensure_ascii=False)
s = m[11]
print("OK sample tail:", s["prompt"][-330:])
print("OK sample neg:", s["negative_prompt"][:300])
