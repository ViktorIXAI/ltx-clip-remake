# Owner feedback log (translated)

Every owner instruction that changed the pipeline, in chronological order.
Original messages were Russian voice/chat messages sent while watching the
cuts delivered on the same day; they are translated to English here and
profanity is removed. "Trigger" = the artifact being reviewed when the message
was sent. Provenance: the owner reviews only the cuts rendered by this
pipeline and delivered over chat; no external references were used.

| # | Instruction (EN, de-profaned) | Trigger → what changed |
|---|---|---|
| 1 | "Sound must be laid on with an exact hit — that is entirely possible with our technology." | Kickoff rule. → frame math: audio cut at exactly N/24 s per scene, 24 fps locked, single master track (`spec/`). |
| 2 | "Make the woman's skin less shiny and sweaty, more velvety; same for the man." | Batch 1 review. → v3 prompt tail + first matte pass experiments (`scripts_history/fix_skin.py`, `render_batch2.log`). |
| 3 | "Now she looks poured-over… bring the photorealism back." | Over-degloss of v3. → proportional matte (gain 0.45, highlight-peak-only) + v4 prompts; measured A/B in `fixreal*.log`. |
| 4 | "Watch the lips — they must sing whenever there is singing." | Cut review. → multi-face MAR tracking + corr≥0.28 gate in `qc_module.py`. |
| 5 | "In the last seconds there are no lyrics, but her lips move like she's whispering." | PART3 review. → silence gate (MAR≤0.30 on non-vocal frames) + v5 prompt clause + negative "mouth moving during instrumental, whispering mouth movements" (`fix_lips5.py`). |
| 6 | "Continue the clip to the end." | Standing order. → unattended batches 6–7 with automatic re-shoot loop. |
| 7 | "As soon as the male chorus passes, assemble the clip without stopping the render flow." | PART_P4 request. → parallel assembly scripts (`partN.sh`) while GPU keeps rendering. |
| 8 | "Show me 18→22 with audio, using the latest take of 22." / 9. "Cut 15 through 25." / 10. "Assemble the full clip from 28 scenes with audio." | Partner-review requests. → parameterized `segAB.sh` with manifest frame math (ST/T/FR printed per cut); `SEG1822`, `SEG_1522`, `SEG_1525*`, `FULL28` (216.17 s, 5188 fr). |
| 11 | "Continue the work, naturally — the next ones." | Keep-going confirmation while cuts were being delivered. → batches continued 29–32. |
| 12 | "GPU 96 °C, CPU 90 °C — verdict 'bad'? How do we cap it, e.g. limit power to 90%?" | Power report during the upscale phase. → verified 0 throttle events, fans 68 %, GPU draw peak 37 W; no cap applied; recommendation recorded (macOS low-power mode would cost ~20 % speed). Upscale was cancelled soon after, so temperatures dropped on their own. |
| 13 | "At 3:57 the woman sits with an ancient man — what happened to the previous one? And why are they all blue — what assembly is this? Return the original partner in the final scene and repaint the whole clip in proper colors." | First master review. → two defects found and fixed: R/B channel swap in the upscale pipe (FINDINGS F9) and headless keyframe → cast drift (F10). Scene 31 re-shot with face keyframe; final assembly rebuilt. |
| 14 | "No 4K needed." / 15. "Not even 1080 needed." / 16. "Do it simpler and faster — for mobile Telegram/TikTok/Twitter it is enough." | Delivery-quality ruling, overriding the spec's 4K plan. → upscale dropped entirely; final = native 1344×768 concat + 41 MB mobile copy (`finish5.log`). Lesson recorded in FINDINGS F11. |
| 17 | "The last two scenes have different men again… use the photo like you did for all the previous scenes." | Second master review. → keyframe-as-identity confirmed as the mechanism (the penultimate scene's keyframe had no heads in frame); replaced with a face-bearing approved frame; re-shoot accepted first seed (`render_s31b.log`). |
| 18 | "Publish the most detailed logs — everything recorded, including power consumption, hardware and its specs, my own conclusions and decision rationale for each step, and all my prompts (translated to English, without profanity)." | This repository. |
