# Timeline (CET, log-derived)

Prehistory (22.11 21:09 → 24.11 02:26, on the NVIDIA box): pi-H3 4-step
night run "neon-water-001" (22 scenes, 305.5 min card for 21), LatentSync
and lipsync-pass attempts, Wan2.2-S2V phase — fully dated in
`docs/PHASE0_PI_H3.md` and in the sibling repo `video-assembly-experiments`.
The table below starts with this repository's engine.

Session began 23.11 evening (spec authoring). Log modification times below are
UTC+1 and come from `logs/` file mtimes on the render machine; they are
ordering-accurate to the minute.

| When | Event | Evidence |
|---|---|---|
| 23.11 eve | MASTER_SPEC + manifest authored (32 scenes, frame math, cast block) | `spec/` |
| 24.11 02:53 | Pipeline setup, first-run errors on LTX-2.3 → switched to 2.5 stack | `logs/pipeline.log`, `logs/models_dl.log` |
| 24.11 03:19 | QC stack setup (MediaPipe landmarker, VLM critic), gemma text encoder pulls | `logs/qc_setup.log`, `logs/gemma_dl.log` |
| 24.11 03:27 | Keyframe extraction from source + QC | `logs/keyframes_qc.log` |
| 24.11 03:55 | First scene tests (try1–3) | `logs/scene_01_try*_stderr.log` |
| 24.11 04:52 | Render test batch | `logs/render_test.log` |
| 24.11 08:22 | Batch 1 full run | `logs/render_batch.log` |
| 24.11 09:28–11:16 | Batches 2–4; re-adopt pass for accepted-but-matted scenes | `render_batch2..4.log`, `readopt_part2.log` |
| 24.11 12:17 | Owner review #1: skin too glossy / wax issues → prompt v3/v4 + matte pass; scene 11 re-shoot chain | `logs/reshoot11*.log`, `scripts_history/fix_style3.py`, `fix_skin.py` |
| 24.11 13:45 | "Real skin" fix round for scene 11 (three passes) | `logs/fixreal*.log` |
| 24.11 14:10 | PART3 cut delivered for review | `logs/part3*.log` |
| 24.11 16:55 | Batch 5c with v4 prompts (photoreal skin restored) | `logs/render_batch5c.log` |
| 24.11 18:22 | Batch 6; owner review #2: "mouth moves at silence like whispering" → silence gate + v5 prompts; scene 17 re-shoot | `logs/render_batch6.log`, `logs/fix17.log`, `scripts_history/fix_lips5.py` |
| 24.11 21:55 | Batch 6b (scenes 18–24 with v5) | `logs/render_batch6b.log` |
| 24.11 23:27 | Cuts 18–22, 15–22 on request (frame math from manifest) | `logs/seg1822.log`, `logs/seg_1522.log` |
| 25.11 01:25–02:55 | Scene 22 saga: gate vs extreme close-up; boost (a2v 5.0) measurably worse; manual accept of best take (corr 0.268) with visual verification | `logs/fix22*.log`, `logs/watch22.log`, `logs/reshoot22.log` |
| 25.11 02:54 | FULL28 cut delivered (216.17 s, 5188 frames) | `logs/seg1525c.log`, `logs/partN.log` |
| 25.11 03:54–07:12 | Batches 7/7b: scenes 26–32 accepted, PROD_DONE | `logs/render_batch7*.log` |
| 25.11 07:25 | Finalize attempt #1: basicsr/torchvision import crash → shim fix | `logs/finish2.log` |
| 25.11 09:19 | Finalize #2 complete: Real-ESRGAN x2 → 1080p master (169 MB) | `logs/finish3.log` |
| 25.11 ~10:00 | Owner review #3 of master: everyone blue (R/B swap in upscale pipe) + wrong man at 3:57 (headless keyframe) | FINDINGS F9, F10 |
| 25.11 10:15–10:20 | Scene 31 re-shoot #1 (text anchor only) + 4K/x4 experiment, then owner cancels upscale entirely ("mobile is enough") | `logs/render_s31.log`, `logs/finish4.log` |
| 25.11 11:04 | Scene 31 re-shoot #2 with face-bearing keyframe → accepted first seed | `logs/render_s31b.log` |
| 25.11 11:10 | Final master v2 (no upscale, rgb-correct, mobile copy 41 MB) delivered | `logs/finish5.log` |

Energy over the whole window: 1.48 kWh monitored, 0 throttle events — see
`power/` and `docs/HARDWARE_POWER.md`.
