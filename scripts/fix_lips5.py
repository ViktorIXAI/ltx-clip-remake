#!/usr/bin/env python3
"""v5 lips tail: sing strictly on the vocal line; in silence the mouth rests."""
import json
OLD = ("her mouth articulates the sung lyrics continuously and naturally "
       "throughout the shot, never sealing or closing her lips while vocals "
       "are audible")
NEW = ("her mouth articulates the sung lyrics in exact sync with the audible "
       "vocals and closes to a calm closed-mouth rest the instant the sung "
       "phrase ends; during instrumental moments her lips stay gently closed "
       "or in a soft smile, never mouthing words")
m = json.load(open("manifest.json"))
n_changed = 0
for s in m:
    if OLD in s["prompt"]:
        s["prompt"] = s["prompt"].replace(OLD, NEW)
        n_changed += 1
    neg = s["negative_prompt"]
    if "mouth moving during instrumental" not in neg:
        s["negative_prompt"] = neg + ", mouth moving during instrumental, whispering mouth movements, mouthing silent words"
json.dump(m, open("manifest.json", "w"), indent=1, ensure_ascii=False)
print("LIPS_TAIL_v5:", n_changed)
