# Findings and lessons (each tied to evidence in this repo)

F1. **Frame math first, prompts second.** Locking 24 fps + 8k+1 frame counts +
vocal cuts at N/24.0 s gave a 253 s clip that ends exactly on the song with
zero mux drift (`spec/`, verified at 04:13 in the first pipeline run).

F2. **Score the best of N faces, not face 0.** Two-person scenes put a silent
male profile next to the singing woman; face-0 MAR destroyed the metric.
Multi-face series in `qc_module.py` fixed it (see comments + scene_11 saga).

F3. **Metrics have valid domains.** corr(MAR,RMS) is deterministic and useful
(0.42–0.72 for confident singing) but breaks for occluded two-face close-ups
(scene_22: corr ceiling 0.268, MAR inflated to 2.75, visually fine). Rule:
manual acceptance with recorded deviation, never metric-driven re-shoot
loops against a bad metric (4 takes × 32 min burned before this rule).

F4. **Gate on silence, not on vocals only.** The "whispering mouth" defect
(lips moving during instrumentals) was caught by the owner's eye before any
gate caught it; the silence gate (MAR≤0.30 on non-vocal frames) plus the
coverage≥0.60 exemption closed it permanently (v5 prompt + negative).

F5. **Near-silent fragments must be vacuously accepted.** Instrumental
scenes burned 3 pointless re-shoots until `rms.max() < 0.01 → pass` —
~75 min of GPU saved thereafter.

F6. **Fixing a gate should not force a re-render.** `re_adopt.py` re-scores
existing takes under the corrected gate and swaps the accepted file — an
accepted-but-rejected take can be rescued in seconds, not 30 minutes.

F7. **Keyframes carry identity.** The headless keyframe of the penultimate
scene free-ran the male character twice (renders_v6/v7 archived on the host);
replacing it with a face-bearing frame from the approved neighbor scene made
the re-shoot pass on the first seed (`render_s31b.log`). Text-only CAST
IDENTITY anchors helped but were not sufficient alone.

F8. **Composition framing decides what can be fixed.** With a headless
keyframe a correct couple scene is physically impossible without inventing
faces; the accepted trade was to keep the couple and change the
staging (beach embrace instead of pier). Identity over mise-en-scène.

F9. **Declare the pixel format you actually produce.** Feeding RGB frames
into an ffmpeg pipe declared `-pix_fmt bgr24` swapped R/B across the entire
upscaled master ("everything is blue"). Detection method that worked in
minutes: compare mean R and B of identical frames in source vs master
(source R=54>B=39, master inverted). Numeric check beats eyeballing.

F10. **Third-party CV stacks rot against torchvision.** basicsr imported
`torchvision.transforms.functional_tensor` (removed); fixed with a shim.
Real-ESRGAN tile stitching dropped `oy/ox` in the tile-size math —
broadcast error only at the right/bottom edges. Both fixed, then the whole
stage became moot — see F11.

F11. **Do not out-engineer the delivery bar.** Owner ruled: mobile/TG/TikTok
grade is enough; the 1080/4K upscale was deleted (`outs = scenes`), which
also deleted the blue-cast bug class and turned a 3-hour finalize into
minutes. Default to the simplest pipeline that meets the stated target.

F12. **Deterministic seeds make gates trustworthy.** Seed 333 reproduced
corr=0.268 bit-identically across independent runs — the A/B comparisons
(a2v boost, keyframe swap) were valid experiments, not noise.

F13. **Energy never limited this workload.** 20+ h of a 22B model on a
128 GB MacBook: 0 throttle events, 45.5 W average, 1.48 kWh total, peak
temps inside the normal corridor (`power/`). Unified memory was the binding
requirement (75 GB model dir, ~60+ GB working set), not clock speed.

F14. **Gated weights are an engineering risk equal to benchmarks.**
LTX-2.3's text encoder (`google/gemma-3-12b`) returned "Access denied.
This repository requires approval." mid-setup (24.11 03:18,
`logs/models_dl.log`); the whole stack swapped to LTX-2.5 within minutes
(`logs/gemma_dl.log`, `model_version=2.5.0` in first-run stderr). Check
license approval state of every required repo before a stack is planned,
not after the transformer is already downloaded.

F15. **"N steps" is per window; wall clock is per project.** The 4-step
pi-H3 still cost 7.7–24.6 min per 192–362-frame scene on a 24 GB card
(sibling repo RUNLOG); Wan2.2-S2V cost 3.1–3.3 card-min per second of
footage in 2.2 s windows; LTX-2.5 here is ≈2–3 card-min/s but in 6–11 s
windows with identity+lip-sync in one pass. For long-form, window length,
offload pressure and shared-card constraints dominate — sampling-step
count does not. This is the arithmetic that moved the project to a
128 GB machine (`docs/PHASE0_PI_H3.md`).

F16. **Our QC gates measured what was easy to measure, not what the viewer
sees.** An independent frame-level audit (`docs/EXTERNAL_AUDIT_GEMINI.md`)
confirmed 4.9/10 while every automatic gate had passed: MediaPipe corr and the
matte formula are blind to time-of-day regressions (02:12, 03:20), an 11 s
motion freeze (03:52–04:03), literal-neon background slop (01:46), hand
artifacts (03:48) and synchronized-to-camera smiles. Goodhart in the wild.
V2 counters: optical-flow motion floor, ArcFace identity lock, lighting
continuity vs a declared timeline, and hard cuts on a downbeat grid.

F17. **One local model was asked to do everything — that was the budget
error, not the hardware.** The MixAI principle we publish says: local for
drafts/unlimited iteration/private data, cloud for the quality ceiling where
cost-per-result wins. A clip with no privacy constraint routed 100% local
gave 32 h and a 4.9 ceiling; the audited hybrid plan (local Route B for 50–60%
of shots, cloud for vocal close-ups and complex physics) projects 8.8–9.6/10
for €25–65 API. Related: MAGI-2 (24.11) fits exactly that vocal/hero route —
API $0.08/s (whole 4-min clip ≈ $20), start/end frames + audio refs — but has
no open weights, so it is a cloud decision, never a local one. The missing
pre-render gate is the keyframe-first **animatic**: the whole defect map above
would have been caught on stills in 5 minutes of human review.
