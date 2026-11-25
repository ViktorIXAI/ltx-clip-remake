# Methodology

How the pipeline was built, and the reasoning behind every component.
All claims cite files in this repo (`logs/…`, `scripts/…`, `spec/…`).

## 1. Source analysis and frame math

Source: 1696×768 @ 24 fps, 253.27 s (owner's own published video). The remake
had to be **frame-exact against the original song** because lip-sync is
evaluated against the vocal track timeline.

Rules locked into `spec/MASTER_SPEC` (translation) and enforced by
`spec/manifest.json`:

- 24 fps exactly; every scene length is `8k+1` frames (145/169/193/217/241…)
  — LTX-2.5 transformer constraint.
- Scene audio = the vocal stem cut at exactly `N/24.0 s` from the same anchor.
  Zero cumulative drift was verified at 04:13.
- Sum of `manifest num_frames` = 6104; the song ends earlier (6078 frames),
  so the master is cut at the song end — the picture tail is trimmed, never
  the audio.

Why: any drift over 2–3 frames becomes visible lip desync at 24 fps; cutting
video to the song is the only place trimming is allowed.

## 2. Generation stack

- LTX-2.5 (22B dev transformer bf16, Gemma-4-12b text encoder, video+audio
  VAE, distilled LoRA-450), ComfyUI-free direct inference on Apple MPS.
- Image conditioning: each scene's keyframe is injected as frame 0
  (`--image <keyframe> 0 1.0 replace`) for composition and identity.
- Audio conditioning (a2v): only for scenes with `lip_sync: true`; the vocal
  stem fragment is the conditioning signal.
- VLM critic: Qwen2.5-VL (MLX) scores every take 1–10 against the spec
  (style, skin, anatomy). `logs/qc_report.json` stores notes.

## 3. Automated QC loop (the core of the experiment)

`scripts/render_scenes_qc.py` per scene: render take → gate → VLM score →
accept or re-shoot (max 3 seeds). The gate (`scripts/qc_module.py`):

1. MediaPipe FaceLandmarker → per-frame MAR (mouth aspect ratio) for every
   face track (multi-face supported since batch 4).
2. `librosa` RMS envelope of the scene's vocal fragment.
3. Pearson corr(MAR, RMS) ≥ **0.28** → lip-sync plausible.
4. Silence ("whisper") gate: on frames where `rms < max(rms.max*0.08, 2e-3)`,
   mean MAR must be ≤ 0.30 — the mouth must be closed when nothing is sung.
5. Instrumental windows are **vacuously accepted** when the whole fragment is
   near-silent (`rms.max() < 0.01`), and the silence gate is skipped when
   vocal coverage < 0.60.

Thresholds and exemptions are the result of measurement, not taste — see
`docs/QUALITY_GATES.md` for the failures that forced each change.

## 4. Skin look: prompt generations v1→v5 + deterministic matte

The owner's look bar: "photorealistic matte skin, no wax, no sweat, no gloss"
(translated). It took five prompt generations and one deterministic post pass:

- v1 raw model output: glossy/oily skin (owner: too sweaty).
- v2 strong de-glss via prompt: "poured/waxy" face — over-correction
  (owner: bring photorealism back).
- v3/v4: proportional approach — keep microtexture, cap specular.
- v5: adds the "mouth closed at silence" clause for tail bars without vocals.
- `scripts/matte_video.py`: luminance-domain de-gloss —
  `L = 0.114B+0.587G+0.299R`, high-pass `hp = L − blur(L,σ14)`,
  `L2 = L − clip(hp,0)·0.45`, then micro-contrast
  `+0.30·(L2 − blur(L2,σ1.2))` and ratio-clamped recolor
  `r = clip(L2/max(L,1), 0.72, 1.12)`. Gain 0.45 is proportional — it removes
  only highlight peaks above the local blurred base, leaving pores/grain.

Decision recorded after the v4→v5 iteration: the look is fixed by **one**
deterministic pass + short prompt tail, not by ever-longer prompt prose.

## 5. Cast identity

- Every scene prompt of the final generation carries the cast block
  (brunette woman / dark-haired man, ~30, short stubble, same wardrobe) —
  `spec/scenes.json`.
- Failure mode found late: the penultimate scene's **keyframe was headless**
  (source framing cut both heads off) → identity free-ran and produced a
  different man twice (`logs/render_s31.log`, `logs/render_s31b.log`).
  Fix: keyframe replaced with a clean face frame from the approved adjacent
  scene, plus `CAST IDENTITY` prompt anchor + negative `old man, elderly,
  grey hair, bald`. Re-shoot passed on the first seed.

## 6. Review cuts and final assembly

- Partner-facing cuts (`scripts/segAB.sh A B TAG`) are built from manifest
  frame sums (never from seconds): ST/T/FR printed per cut, audio muxed with
  exact `-t`, e.g. scenes 15–25 → `T=93.458333, FR=2243`.
- Final assembly (`scripts/finish_movie.py`): concat of accepted scenes
  (copy) + single `full_mix.wav` → AAC 192k + faststart. An earlier variant
  upscaled via Real-ESRGAN x2; it introduced a blue-cast (see FINDINGS F9)
  and was dropped for the final: owner ruled mobile resolution is sufficient.

## 7. Energy/thermal observation

A 60-s telemetry loop (`power/`, monitor log) recorded system watts, battery
flow, throttle and speed-limit flags for the whole 32 h. Purpose: prove the
128 GB unified-memory box was not thermally compromised during 20+ h of
continuous 22B generation. It wasn't (0 throttle events, peak 90 W).
