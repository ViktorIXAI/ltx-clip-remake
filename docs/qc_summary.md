# Final QC report (per-scene)

Source of truth: `logs/qc_report.json` (written by the automated runner at finalize time). `corr` = Pearson correlation between MediaPipe mouth-openness (MAR) and vocal RMS envelope; `—` = lip-sync gate vacuous (instrumental / near-silent fragment). Automated attempts recorded: 32. Scenes scene_09, scene_12, scene_18, scene_24 went through manual re-shoot/re-adopt chains afterwards and are absent from this last report write — their outcomes are in the logs (see TIMELINE). Scenes 31 re-shoot outcomes: `render_s31.log`, `render_s31b.log`.

| scene | attempts | final lip_ok | final corr | final VLM score |
|---|---|---|---|---|
| scene_01 | 1 | True | — | 8 |
| scene_02 | 1 | True | — | 8 |
| scene_03 | 1 | True | — | 8 |
| scene_04 | 1 | True | — | 8 |
| scene_05 | 1 | True | — | 8 |
| scene_06 | 1 | True | — | 8 |
| scene_07 | 1 | True | — | 8 |
| scene_08 | 1 | True | — | 8 |
| scene_10 | 1 | True | — | 8 |
| scene_11 | 1 | True | 0.715 | 8 |
| scene_13 | 1 | True | — | 8 |
| scene_14 | 1 | True | — | 8 |
| scene_15 | 1 | True | — | 8 |
| scene_16 | 1 | True | — | 8 |
| scene_17 | 2 | True | 0.425 | 8 |
| scene_19 | 1 | True | — | 8 |
| scene_20 | 1 | True | — | 8 |
| scene_21 | 1 | True | — | 8 |
| scene_22 | 4 | False | -0.261 | 8 |
| scene_23 | 1 | True | 0.496 | 8 |
| scene_25 | 1 | True | — | 8 |
| scene_26 | 1 | True | — | 8 |
| scene_27 | 1 | True | — | 8 |
| scene_28 | 1 | True | — | 8 |
| scene_29 | 1 | True | — | 8 |
| scene_30 | 1 | True | — | 8 |
| scene_31 | 1 | True | — | 8 |
| scene_32 | 1 | True | — | 8 |
