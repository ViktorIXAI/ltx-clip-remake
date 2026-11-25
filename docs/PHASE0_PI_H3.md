# Phase 0 — before this repo: pi-H3 on the NVIDIA box (22–24.11)

This repository is the second engine attempt on the same creative goal
(a full local music video for the owner's song). The first attempt ran on a
different machine with a different model. This file records it completely,
from the owner's first request, because the constraints measured there are
exactly what forced the switches to this repo's machine and model.

Full technical notes of that phase (scene tables, cut-detector math,
assemblies) are published separately in the sibling repo
`ViktorIXAI/video-assembly-experiments` (README.md + RUNLOG.md), same
standing rule: no media, no weights, no host addresses.

## The model the owner asked for: pi-H3 (released 21.11)

- **MiniMax H3** (MiniMax): joint video+audio DiT; FL2VA conditioning =
  text + first frame + last frame. Comfy-Org pack:
  `minimax_h3_fl2va_pruned_int8_convrot.safetensors` 20,970,379,616 B;
  video VAE `minimax_h3_video_vae_int8_convrot` 2,811,065,184 B;
  audio VAE `minimax_h3_audio_vae_fp32` 605,254,808 B; text encoder
  `qwen3vl_32b_minimax_h3_nvfp4_awq` 15,687,142,551 B (Qwen3-VL 32B base).
- **pi-H3 1.0** (Stanford / Lakonik: Chen, Cai, Song, Wetzstein, Yan,
  Guibas): data-free few-step distillation of H3 — **2 or 4 sampling
  steps**, with DWD variants ("decode without a decoder": the last
  denoising step predicts pixels, skipping the video VAE). Weights,
  inference code and ComfyUI support (ComfyUI-piFlow) all released
  **2026-11-21** — the "released November 21, video in four passes"
  reference from the owner. Adapters used:
  `pi_h3_4step_dwd_adapter_int8_convrot.safetensors` 2,192,176,240 B
  (the 2-step twin also downloaded; the 4-step file rendered every scene).
- Stack: ComfyUI 0.46.0 + ComfyUI-piFlow git `e0ca46f`, PyTorch
  2.14.1+cu130.

## Machine: P2005 (the household-LLM box)

RTX 5090 Laptop, 24,463 MiB, firmware power cap 175 W, 64 GB RAM,
Ubuntu 24.04, driver 615.71.09 / CUDA 13.4. The same GPU hosts the house
LLM brain; to load the 21 GB H3 trunk the brain process was **parked**
for this run (recorded 22.11 21:21:08–21:21:13, VRAM 23,933 → 266 MiB).
No power telemetry was captured for this phase — the energy monitor
(`power/`) starts with the Mac.

## Owner's kickoff (22.11 ~21:23, translated, condensed)

"Once everything is downloaded, installed and the model's tools are
verified, give me a detailed readiness report — what was downloaded, what
is done, that you are ready — then execute the job below and estimate the
time on my hardware. Task: autonomously generate a complete 4:10 (250 s)
music video 'Neon Over the Water' via the local ComfyUI API on the pi-H3
model and assemble the final video with the original audio via ffmpeg.
768p (20:9, multiples of 16/32), 24 fps, steps=4, DWD on, guidance 1.0.
Check whether the workflow supports reference-image conditioning: if yes,
generate ref_woman/ref_man and feed them per scene; if not, use text mode
with a hard global style+cast block prepended to every scene prompt.
22 scenes, exact per-scene durations [full list in the message]. Skip
existing scene files >1 MB on restart, log per-scene render time and peak
VRAM, auto-downgrade to 576p/480p on OOM."

## Run: neon-water-001 (22.11 21:09 → 23.11 03:25)

- 21:09–21:40 — ComfyUI clone, torch install, model pulls (sizes above);
  smoke render returned a file. First real bug: ComfyUI history stores the
  mp4 under `outputs.images` (`metadata.kind == video`), not a `videos`
  key — treating a missing `videos` key as failure discarded one finished
  render.
- 22:04 — scene 1 (about 22 min sampling). 22:17:57 → 03:23:36 — one
  queue of scenes 2–22 at 1696×768, 192–362 frames each;
  **305.5 minutes of card time for 21 scenes** (7.7–24.6 min/scene).
- 03:23:49 — assembly #1 (89,092,656 B) with the song mixed last
  (`-shortest`); 03:25:17 — assembly #2 (84,173,327 B) with a cut
  detector for first/last-frame conditioning jumps + stretch-back to
  original durations. CPU previews of finished prefixes (5/8/12/13
  scenes) built while the renderer kept running.

## What the H3 line could not do (the crisis that shaped this repo)

pi-H3/H3 adapters are **FL2VA only**: no reference-image identity
conditioning, and **no audio-to-video conditioning**. Mouths cannot be
generated from the vocal track; the song can only be mixed onto the
finished picture. The owner's next brief (23.11 07:38, "hybrid-ai-001",
handed over with "do the whole job, do not ask again") targeted exactly
that. Same-day response chain, from directory mtimes on the box:

- 08:21 `hybrid_ai_v2` experiments; 09:20–10:35 LatentSync clone + venv
  (post-hoc lip sync); 11:11 `hybrid_lipsync` pass;
- 11:30–11:41 — speech-to-video route pulled: **Wan2.2-S2V-14B**
  `wan2.2_s2v_14B_fp8_scaled` 16,394,832,474 B + `umt5_xxl_fp8`
  6,735,906,897 B + `wav2vec2_large_english_fp16` 630,997,322 B +
  `wan_2.1_vae` 253,815,318 B;
- 11:41 first S2V batch crashed mid-render; 16:53 `hybrid_h3_voice`
  audio-conditioning test on H3; 24.11 02:11–02:26 S2V re-run:
  **7.8 min per 57-frame window, 6.8 min per 53-frame window**
  (≈3.1–3.3 card-minutes per second of footage, 2.2–2.4 s windows).

## Switch 1 — different computer (P2005 → MacBook Pro M5 Max)

Three measured constraints, not preference:

1. **Shared card.** The NVIDIA box is the house-brain box; every serious
   render requires parking the brain (recorded above). The remake needed
   ~50 render attempts — unacceptable on the brain machine. The MacBook
   carries no brain, so the render fleet runs alongside the LLM at full
   speed (see `HARDWARE_POWER.md`).
2. **24 GB VRAM.** H3 trunk (21 GB) + Qwen3-VL-32B (15.7 GB) only fit via
   INT8/NVFP4 quantization; Wan-S2V (16.4 GB) + umt5-xxl (6.7 GB) forced
   offload and ≤57-frame windows. At 3.1–3.3 min of card time per second
   of footage, one clean pass over the 6,104-frame target ≈ 13–14 hours
   before retries.
3. **One-model capability.** Identity keyframes + audio-driven lip sync +
   first/last-frame continuation in a single pass: H3 offers only the
   third; Wan-S2V only the second (slowly). LTX-2.5 offers all three, and
   its 75 GB model dir fits 128 GB unified memory with no offload —
   6–11-second windows at 17.7–32.3 min each (≈2–3 card-min/s of footage
   but 3–5× longer windows and one pass instead of a model relay).

## Switch 2 — LTX-2.3 → LTX-2.5 (24.11 02:53–03:21, this repo)

- The first pulls on the Mac were the LTX-2.3 set (`ltx-2.3-22b-dev`,
  `ltx-2.3-22b-distilled-lora-384-1.1`, spatial upscaler x2 1.1); that
  era's runner is `scripts_history/render_scenes.py`.
- LTX-2.3's text encoder (`google/gemma-3-12b`) failed mid-setup:
  **"Access denied. This repository requires approval."**
  (`logs/models_dl.log`) — a gated-weights wall, not a quality verdict.
- The LTX-2.5 set (22B dev transformer bf16, distilled **LoRA-450**,
  video+audio VAE, latent spatial upscaler x2, text encoder
  `gemma4-12b-with-proj-ltx-2.5-bf16`) pulled fine at 03:18–03:21
  (`logs/gemma_dl.log`). All renders from `render_test.log` onward ran
  2.5; checkpoints self-declare `model_version=2.5.0` in
  `logs/scene_01_try*_stderr.log`.
- The first failures under 2.5 were our math, not the model:
  "Resolution (720x1280) is not divisible by 64" → the frame-math rules
  in `spec/MASTER_SPEC.md` (multiples of 64, 8k+1 frames).
