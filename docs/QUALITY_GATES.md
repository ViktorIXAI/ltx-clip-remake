# Quality gates: math, evolution, measured results

Implementation: `scripts/qc_module.py` + `scripts/render_scenes_qc.py`.
Per-scene results: `docs/qc_summary.md`; raw: `logs/qc_report.json`.

## Lip-sync gate

- MAR (mouth aspect ratio) per frame from MediaPipe 478-point mesh
  (inner lips 13/14, mouth corners 78/308), one series per detected face.
- Vocal RMS envelope of the exact scene audio fragment (librosa).
- **corr(MAR, RMS) ≥ 0.28 → lip-sync plausible.** Measured noise floor with
  mouth closed ≈ 0.04; confident singing 0.42–0.72 (see qc_summary:
  scene_11 0.715, scene_09 0.549, scene_17 0.425).
- Multi-face: score is the best of the faces, so a silent male profile does
  not veto the singing woman.

## Silence ("tail") gate

- Vocal mask: `rms >= max(rms.max()*0.08, 2e-3)`.
- On non-vocal frames mean MAR must be ≤ 0.30 ("no open-mouth whispering").
- **Coverage exemption:** applied only when vocal coverage ≥ 0.60 — quiet
  singing is indistinguishable from breathing by RMS and the gate produced
  false failures before the exemption (logs `fix17.log`, `seg_1525*.log`).

## Vacuous gate

- If the fragment's `rms.max() < 0.01` (instrumental window), lip-sync is
  vacuously accepted (`corr=None` rows in qc_summary). Before this rule,
  instrumental scenes 18/24 burned 3 pointless re-shoots (~75 min GPU).

## VLM critic

- Qwen2.5-VL (MLX) inspects 5 sampled frames against an artifact checklist
  (skin, hands, teeth, outlines, text). Every accepted take scored 8/10.

## Re-shoot policy

- Seeds 42 → 1337 → 9001; early exit on `lip_ok && score>=8`.
- Self-heal boost (a2v strength 3.0, seed 777) when all 3 fail. Measured
  effect on the difficult scene_17/22: boost corr values 0.084 / 0.013 /
  −0.261 — **a2v boost did not help**, the decisive levers were the
  open-mouth keyframe (`s11/s17/s22_openmouth_key.py`) and the coverage
  exemption.

## Where the metric is wrong (documented deviation)

Scene_22 "forehead-to-forehead" extreme close-up: both mouths partly
occluded → MAR inflates (max 2.75), corr never exceeds 0.268 across
seeds 2024/7/333/42 while the take is visibly singing. Seed 333 reproduced
corr=0.268 exactly in two independent runs — the metric is deterministic,
just not applicable to occluded two-face close-ups. Decision rule adopted:
manual visual acceptance with the deviation recorded. scene_24 failed corr repeatedly (−0.481, −1.0; night-pier scene with sparse
vocals) and was rescued via the manual re-adopt chain after the coverage
exemption; it is absent from the final report write (see qc_summary note).
