# Hardware, software stack, energy

## Machine (render host)

| Item | Value |
|---|---|
| Model | MacBook Pro, Mac17,7 (source: `system_profiler SPHardwareDataType`) |
| SoC | Apple M5 Max, 40-core GPU |
| Memory | 128 GB unified |
| OS | macOS (Apple Silicon), inference on PyTorch MPS backend |
| IP / user | local network, redacted |

## Software / model stack (measured from the venv and logs)

| Component | Version / artifact |
|---|---|
| PyTorch | 2.15.0 (MPS) |
| ffmpeg | 9.1 (Homebrew) |
| MediaPipe | 1.2.3 (FaceLandmarker, 478-pt face mesh) |
| VLM critic | mlx-vlm 0.8.1 + Qwen2.5-VL local weights (`models/vlm_critic`) |
| LTX-2.5 | 22B dev transformer bf16, Gemma-4-12b text encoders (q8_0/q4_0), video+audio VAE, distilled LoRA-450; `models/ltx-2.5/` = 75 GB (download log: `logs/models_dl.log`) |
| Real-ESRGAN | x2plus weights (experiment only; final has no upscale stage) |
| Audio | ffmpeg extraction; 44.1 kHz full_mix + vocal stems |

## Energy and thermals

Telemetry: `power/mac_stats.csv` — samples every ~65 s over 32.4 h spanning
the entire render/fix period (1796 rows), `power/monitor.log` is the daemon log,
`power/mac_last.txt` a recent window report.

Measured over the full window:

- Average system power: **45.5 W**, peak sample: **90 W**.
- Total energy: **1.48 kWh** in 32.4 h (battery + AC; battery % recorded).
- **Throttle events: 0; CPU frequency limiter: 100 %** — the SoC never
  power-throttled during 20+ h of continuous 22B generation.
- During the heaviest stage (Real-ESRGAN upscale pass, later removed):
  CPU peak 90 °C, GPU peak 96 °C, fans 68 % of max, GPU draw peak 37 W —
  inside Apple's normal operating corridor (junction limit is far higher,
  hardware would clamp before damage).

Derivation notes:
- `sysW` is `powermetrics` system-on-chip power; energy = Σ sysW × 65 s.
- GPU power on Apple Silicon reports ANE+GPU cluster power; figures are a
  lower bound for total package draw, which is why sysW (45.5 W avg) exceeds
  the per-GPU figure.

## Cost estimate (for reference)

1.48 kWh × typical EU domestic tariff (~€0.30/kWh) ≈ **€0.45 of electricity**
for the entire 253-second video. Wall-clock cost, not GPU-time-only.
