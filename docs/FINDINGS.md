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
