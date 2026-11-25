# LTX-2.5 music-video remake — full experiment log

End-to-end record of a 253-second music-video remake generated with **LTX-2.5**
(22B transformer, audio-to-video lip-sync) on a single **Apple M5 Max / 128 GB**
MacBook Pro. 32 scenes, an automated QC loop (lip-sync gate + VLM critic), five
prompt generations (v1→v5), a deterministic skin-matte post pass, and a
user-in-the-loop review cycle. This repo contains every text artifact that was
produced: spec, manifests, scripts (final + historical iterations), raw run
logs, the QC report, and machine power telemetry. No media files are published
(source footage and renders are third-party / derivative content).

## Headline numbers

| Metric | Value |
|---|---|
| Final runtime | 253.27 s, exactly the song's end (frame-accurate, 24 fps) |
| Scenes | 32, all frame counts of the form 8k+1 (LTX constraint) |
| Render attempts recorded | 32 in the automated report; ~50 incl. manual re-shoots |
| Wall time (model download → final master) | ~32 hours, mostly GPU |
| Machine energy in monitored window | 1.48 kWh over 32.4 h (avg 45.5 W, peak 90 W) |
| Thermal throttling events | 0 |
| Final delivery | 1344×768 @ 24 fps, ~41 MB H.264 (mobile/TG/TikTok grade) |

## Pipeline (one line per stage)

source clip → storyboard + frame math (`spec/`) → keyframe extraction →
LTX-2.5 i2v+a2v render (seed lottery 42/1337/9001) → automated QC
(lip-sync gate + VLM critic) → skin-matte pass → accept / re-shoot loop →
per-request segment cuts → concat + single audio track (`full_mix`).

## Repo map

- `docs/METHODOLOGY.md` — how the pipeline was designed, why each part exists.
- `docs/TIMELINE.md` — dated sequence of every batch, fix and decision.
- `docs/USER_FEEDBACK.md` — every owner instruction, translated to English
  (profanity removed), with the review that triggered it and what changed.
- `docs/QUALITY_GATES.md` + `docs/qc_summary.md` — gate math, thresholds and
  their evolution; per-scene results.
- `docs/HARDWARE_POWER.md` — machine, model stack, versions, energy/thermal data.
- `docs/FINDINGS.md` — lessons, each tied to the log lines that prove it.
- `spec/` — master spec (English translation), `manifest.json`, `scenes.json`
  (the actual prompts fed to LTX, final v5 state).
- `NOTICE.md` — what is intentionally not published and why.
- `scripts/` — final toolchain (runner, QC gate, matte, segment cutter, finisher).
- `scripts_history/` — superseded iterations (skin/style/lipsync fix versions v1–v5).
- `logs/` — raw run logs (message text machine-generated; human-readable
  fragments translated RU→EN, numbers/identifiers unchanged; paths/usernames
  redacted).
- `power/` — 60-second-interval machine telemetry CSV + monitor reports.

## Result verdict

Photoreal matte skin (after two failed extremes), mouth closed on instrumental
silence, lip-sync accepted where measurable, one accepted scene with a weak
metric but visually-correct singing (documented in FINDINGS), final scenes
cast-consistent after the keyframe-identity fix. Energy and thermals stayed in
normal range the entire time; no throttling, no crashes that were not
diagnosed and fixed the same day.
