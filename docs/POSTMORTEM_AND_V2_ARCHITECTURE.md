# CLARYEL Video Factory: deep post-mortem of the `pi-H3 → LTX-2.5` experiment and the V2 architecture for a 10/10 target

> **Analysis date:** 25 November 2026
> **Audit object:** the full production cycle of the *«Neon Over the Water»* clip (22–25.11.2026, phases `P2005 / pi-H3` → `Wan2.2-S2V` → `M5 Max / LTX-2.5`, commit `58680eb` in `ViktorIXAI/ltx-clip-remake`), the final video master (04:12), and the business context of `CLARYEL S.R.L.S.` (`claryel.com`).
> **Purpose:** inclusion in this repository + a direct technical specification for AI agents (Hermes and others) to rebuild the pipeline along two commercial tracks.

This is the **complete external audit** authored by Google Gemini ("Gemini Neon"), received by the project owner as a file and published through the Hermes agent (translation to English, secret gate, commit). The body — defect map, post-mortem, both pipelines and the YAML spec — is the auditor's text, reproduced in translation with all numbers as in the source. A condensed earlier copy of sections 1–6 is in `docs/EXTERNAL_AUDIT_GEMINI.md`; this file is the canonical full version, including the previously truncated sections 7–8.

---

## 1. Source verification and honest access boundaries (fact-check log)

Recorded below is strictly what was confirmed by search, video viewing and notebook logs — and what had no direct access.

### 1.1 Confirmed origin thread on X (starting point of the experiment)
- **Found and confirmed:** the original Chinese post by **`@pixelaigc`** dated **21–22 November 2026** — `https://x.com/pixelaigc/status/2124520344778313850` (linked repository: `https://github.com/pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow`).
- **Facts from the post:** local generation of a 30-second video **with sound** on an **RTX 3060 12 GB** (+24 GB RAM) via the **`pi-H3`** model (2 steps, 480p, 1071 s ≈ 17.85 min) driven by a 7-block director prompt (dialogue after *«Lust, Caution» / 《色戒》* with FACS expression codes).
- **`pi-H3` release dating:** LakonLab announcement/blog (Hansheng Chen et al.) — 10–11 November 2026 (`hanshengchen.com/blog/pi-h3/`, `github.com/Lakonik/LakonLab`); public release of weights and ComfyUI nodes — 21 November 2026. The CLARYEL experiment started **the next day** (22.11.2026, 21:00 CET).

### 1.2 Confirmed facts about the `CLARYEL` business (`claryel.com` / `claryelsolar.com`)
From indexed site pages (`claryel.com/`, `/configurations/`, `/configurations/level-1/`, `/level-2/`, `/level-3/`, `/software/`, `/mixai/`, `/news/`, `/it/usage/`, `/evidence/`, `/legal/security/`, `/ru/team/`, `claryelsolar.com/`):
- **Legal entity:** `CLARYEL S.R.L.S.`, Via Leonardo Da Vinci 26, 22073 Fino Mornasco (CO), Italy; VAT `04258140138`, ATECO `62.10.00`, participant of *Bando Nuova Impresa 2026 — Regione Lombardia*.
- **Current market:** sales are officially **B2B only (VAT/P.IVA holders)** — the FAQ states private customers are not served directly yet, while `/mixai/` and the adjacent `CLARYEL Solar` line carry a smart-home / private energy-automation strategy.
- **Product line (`CLARYEL Box`) and transparent prices (VAT incl.):**
  - **Level 1 — Local AI Start (€999, 12-month installment):** Intel Xeon E5-2690 v4 (14c/28t), ASUS Z10PA-U8, 64 GB DDR4 ECC, NVIDIA Tesla P100 16 GB HBM2 (used base + new 1 TB NVMe Patriot VP4300 Lite, ASUS Prime 750 W PSU, case, cooling). Private assistant and document search for a small office.
  - **Level 2 — Local AI Business (€2,999, 12-month installment):** all-new — Intel Core Ultra 7 270K Plus (24c), ASUS Pro Q870M-C (Intel vPro), 64 GB DDR5 (2 free slots), AMD Radeon RX 9070 16 GB, 2 TB PCIe 5.0 NVMe Lexar NM1090 PRO. The office's local core: automation, smartphone remote access.
  - **Level 3 — Local AI Pro (from €7,000, individual configuration):** high-performance systems for heavy loads (site examples: Mac Studio M3 Ultra 256 GB, MacBook Pro M5 Max 128 GB) + storage, backups, UPS.
- **Entry and support pricing:** consultation with business pre-analysis and architecture presentation — **€81.15 + VAT (€99.00 incl. VAT)**. Support plans: **Basic €0** (included, 24/7 AI agents + 1-year warranty), **Plus €29.99/mo**, **Pro €149.99/mo** (specialist, ≤4 business-hours response, critical failures ≤1 h), **Individual from €500/mo** (24/7, hardware-replacement-within-24h goal).
- **Key product/software USPs (`claryel.com/software/`, `/it/usage/`, `/mixai/`):**
  1. **MixAI philosophy (hybrid AI):** *"We don't try to prove local or cloud AI is better… what matters is the cost of the final result, not the tools."* Data processed locally by default with no token limits or quotas; cloud calls pass an **egress privacy filter** (strips personal data and trade secrets, requires explicit user confirmation before sending).
  2. **Voice control in 100+ languages + a real ERP-audit case:** a published internal case — a voice query on IT spending found fake invoices and duplicates (from ≈€54,691, after human-confirmed cleanup: 188 valid invoices / €36,993.58, with change history and rollback).
  3. **Emergency data-encryption button:** instant data lock, key destruction, restore only via backup keys.
  4. **Free website included (voice-managed via the agent)**, **Home Assistant** integration, EU regulatory posture (GDPR, CNIL, NIS2, EU AI Act Art. 50).
  5. **The brand's honest engineering voice (`@uctive`):** confirmed public threads/quotes (`vramcalculator.com`, `note.com`, YouTube breakdowns, `claryel.com/news/`): the DDR5→DDR4 practicality switch (status/2122988375888040023, 18.11.2026), the 6-part Strata-vs-Basalt benchmark on RTX 5090 Laptop (status/2123323827144814599, 19.11.2026), GPU price-rise monitoring (+33% in 45 days), the deploy paused for an isolation audit (Docker vs KVM/Kata/gVisor, 09.11.2026), the honest advice "test your model free in the cloud first, then buy hardware" (08.11.2026), the "€135 garage AI server" experiment (12.11.2026).

### 1.3 Access limits (recorded honestly)
- Direct parsing of the closed X/Twitter timeline is unavailable; the specific tweet `x.com/uctive/status/2124515830943641634` was not Google-indexed at audit time, so its thesis is taken strictly from the owner's task statement and the confirmed `claryel.com/mixai/` article.
- The `ViktorIXAI/ltx-clip-remake` repository was published 25.11.2026 at 21:44 CET (~1 h before the analysis) and was not yet search-indexed; direct URL file reading was limited by the environment. The audit therefore relies on **exact metrics and the artifact list of commit `58680eb` from the owner's report**, the 22–25 November phase logs, and **direct frame-level analysis of the attached 04:12 video**.

---

## 2. Frame-by-frame audit of the final clip (04:12) — verification of the 4.9/10 score

The attached video (04:12, track *«Neon Over the Water»*) was watched in full. The **4.9/10** score from the previous chat is fully confirmed by visual facts — the defect and success map by timecode follows.

### 2.1 Exact map of visual and editing defects

| Timecode | Defect category | What actually happens on screen |
| :--- | :--- | :--- |
| **00:21** | Editing break / geometry drift | Abrupt change of orientation of the pier, gazebo and lamppost across a cut on the same sunset background. |
| **00:28–00:34**, **02:25–02:35**, **03:36–03:45** | "Plastic / oily" skin (AI gloss) | On extreme close-ups (especially the macro eye/nose-bridge at 02:25–02:35) forehead and cheek skin has an unnatural wet-lacquer specular sheen; the skin-matting formula did not remove the synthetic micro-shine. |
| **00:54** | Local face artifact | Brief visual defect/spot on the man's forehead during a head turn. |
| **00:56–01:01**, **01:09–01:15** | Lipsync + appearance drift | At 00:58 the heroine's face visibly "ages" and changes jawline; at 01:09 the mouth opens into an unnatural hypertrophied "O" without matching the sung syllables (*"Let's have dance fight..."*). |
| **01:04–01:08**, **02:10–02:12**, **03:20–03:27** | **Critical time-of-day logic break** | The clip jumps back and forth in time: from deep night city (01:03) crossfading back into bright sunset (01:05); on the boat deck the night city (02:10) dissolves into bright daylight sunset inside the same scene (02:12); after night lasers (03:19) a hard revert to a sunny golden beach (03:20). |
| **01:18–01:19**, **01:27–01:30** | Dirty crossfades and loop repeat | Double-exposure "ghosts" dissolving large faces (01:18); at 01:30 a repeated loop of the kiss under the neon arch. |
| **01:33–01:38**, **03:28–03:35** | "Sticky" AI dance physics | Mechanical arm-waving and stiff gestures, typical of diffusion video without a choreographic reference. |
| **01:45–01:51**, **03:04–03:11** | **Literal AI-slop in backgrounds** | Direct reaction to the words *"neon lights over the water"*: at 01:46 absurd glowing neon squiggles on poles stick out of the sea; at 03:04 cheap pink-blue laser sheets fire vertically out of the water. |
| **02:00–02:09** | Hero identity drift | Against the night skyscraper the man's profile changes noticeably (different nose shape and beard), after which the two smile motionlessly at each other nose-to-nose for 7 seconds. |
| **03:14–03:19** | Cliché "look at camera + wink" | Typical neuro-reel pattern: both turn in sync into the lens and freeze with glossy smiles. |
| **03:46–04:03** | **Anatomy break + cartoon background + frozen frame** | A painted Milky Way with huge white "snowflake" dots in the sky; on the man's left arm around her waist (03:47–03:50) an unclear white glove/bandage appears and morphs; from **03:52 to 04:03 (~11 seconds!) the frame is almost completely frozen**, killing the finale's dynamics. |

### 2.2 What genuinely worked well (the base to keep)
- **00:00–00:14** (sunset prologue and kiss by the rocks), **01:39–01:44** (low angle of bare feet in water with reflections) and **04:04–04:12** (pre-dawn forehead-to-forehead finale) look organic and cinematic.
- **Costume consistency** (champagne-toned silk dress + open black shirt) is held stably across the whole 4+ minutes.
- **Engineering discipline of the release:** power telemetry (1,796 samples, 1.48 kWh ≈ €0.45, 0 throttling on M5 Max), reproducible code, clean `Gitleaks`-gated publication — exemplary engineering culture.

---

## 3. Deep process post-mortem (22–25 November 2026): what was done wrong

In three days the project went through three architectural switches:
1. **Phase 0 (`P2005` / RTX 5090 Laptop 24 GB + `pi-H3`):** 22 scenes, 305.5 GPU-minutes (~5.1 h pure render). Revealed: no audio-to-video lip-sync, the reference frame causes a jump at scene start, rendering forces parking the primary "brain" (Basalt) from 23,933 MiB down to 266 MiB VRAM.
2. **Phase 0.5 (`LatentSync` → `Wan2.2-S2V-14B`):** 3.1–3.3 GPU-min per 1 s of footage, windows of 53–57 frames (~2 s), visuals of the August-2025 generation.
3. **Phase 1 (`MacBook Pro M5 Max 128 GB` + `LTX-2.5 22B`):** 32 scenes, 253.27 s, ~32 hours from weight download to master, ~€0.45 of electricity, automatic QC gates (`MediaPipe`, `Qwen2.5-VL`).

### Main verdict: six systemic errors that made 32+ hours land at 4.9/10

1. **The "local purism" trap (direct contradiction of our own MixAI philosophy).** `claryel.com/mixai/` formulates the ideal principle: local hardware for private data, drafts and mass iteration without quotas; cloud when the quality ceiling and cost-of-result matter. This experiment had no trade secret, yet one local model (`LTX-2.5`) was loaded with everything at once: vocal lip-sync, choreography, macro skin and a 4-minute storyline. Result: 32 hours of waiting and a 4.9/10 ceiling instead of a hybrid render of the problem 25% of scenes for €15–€30.
2. **Architectural error of feeding audio into the video model (root cause of the 4/10 lipsync).** In `LTX-2.5` (confirmed both by our report — `scene_22 corr 0.268`, `boost −0.261` — and independent late-2026 community tests) feeding the **mixed music track** (trance beat + bass + reverb + vocal) makes the model hallucinate abstract mouth motion; it cannot cleanly extract vocal phonemes through a dense mix. Vocal shots require prior stem separation (**BS-RoFormer / Demucs** → clean dry vocal) and a specialized performance engine.
3. **Missing "Keyframe-First Animatic" stage (blind video generation).** Generating 22–32 video clips straight from text and two portraits inevitably produces face drift, time-of-day jumps and empty repeats. In professional 2026 AI production **no video render starts before a storyboard of static Start/End keyframes is approved** and assembled into a slideshow (animatic) exactly under the MP3. Fixing light, skin, stray neon poles and day/night at the image level takes 15 minutes, not 32 hours.
4. **Proxy-metric illusion in the QC gates (Goodhart's law).** The automatic gates (`MediaPipe corr`, the skin-matting formula) honestly measured *technical* passability but were blind to the main neuro-slop triggers: unnatural smiles, the 11-second motion freeze (03:52–04:03), absurd neon rods in water (01:46), the white-glove hand artifact (03:48) and night→day regressions (02:12, 03:20).
5. **"Literal illustration" direction and "glossy casting".** The prompt "beautiful 25-year-old European woman + 28-year-old European man on a sunset beach" across 32 consecutive scenes guarantees a template AI postcard. The viewer tires by second 90: no dramatic conflict/action, no shot-size and rhythm variation, and the lyrics (*neon lights over the water*) are illustrated word-for-word.
6. **Assembly/editing errors:** long crossfades on close-ups (01:18, 01:27) create dirty "double exposure", and the lack of hard cut-to-bar-grid (BPM/downbeat) locking drains the electronic track's percussive drive.

---

## 4. Track 1: CLARYEL business commercial pipeline (10–90 seconds)

### 4.1 Strategic rule for B2B advertising (`claryel.com`)
The audience is SMB owners in Italy/Europe, accountants, managers with P.IVA considering €999–€7,000+ hardware and €29.99–€500/mo subscriptions.
**Main risk:** glossy "cyberpunk AI" with model faces and painted neural-network servers causes instant B2B distrust (*"if even their ad is fake, what about their server?"*).
**The 10/10 formula for CLARYEL — the hybrid "Real + MixAI Commercial Pipeline":**
- **40% of the frame — reality (maximum trust):** real photos/short shoots of the actual `CLARYEL Box` chassis (Level 1/2/3), the real voice-answer interface and real invoice-audit screen, clean programmatic vector graphics (Remotion / Manim / FFmpeg alpha overlay — **total ban on generating text inside video models**).
- **60% of the frame — maximum-photorealistic AI scenes with living "ordinary" people:** not photomodels but realistic European entrepreneurs aged 32–52 (light wrinkles, natural office light, ordinary clothing, Lombardy/Milan-style offices, a car, a workshop, a solar farm for `CLARYEL Solar`).

### 4.2 Optimal tool stack (MixAI for video, November 2026)

| Stage | Tool (local vs cloud) | Why exactly this | Budget per 30-s spot |
| :--- | :--- | :--- | :--- |
| **1. Script & storyboard (EDL)** | LLM (Claude / Gemini / local Qwen) | Hard 3-second hook, structure *Pain → Contrast → Proof → Offer*, shot timing 1.5–3.5 s. | €0 |
| **2. Voiceover / dialogue** | ElevenLabs / Cartesia / local TTS (IT / EN / RU) | Crystal diction, live tempo, each line's length exact to the millisecond **before** any video generation. | ~€0.5–€1 |
| **3. Approved Start/End keyframes** | Local Flux / Qwen-Image or cloud GPT-Image / Imagen + real CLARYEL Box photos | 100% control of photorealism, matte skin, light, the real CLARYEL Box chassis (image-to-image / compositing) **before** the video render. | €0–€2 |
| **4. Draft motion / animatic** | **Local:** `LTX-2.5` (M5 Max) or `pi-H3` (RTX 5090) | Free check of rhythm, angles, scene durations. | €0 |
| **5. Final hero-shot render (MixAI)** | **Cloud via API:** `Veo 3.1` (4–8 s, reference dialogue & cinematic realism), `Seedance 2.5` (up to 30 s, up to 30 references, 4K, exact brief-following), `Kling 4.0` (precise camera choreography, ~2.4× cheaper than Seedance at 1080p) | Guaranteed removal of "plastic", sticky physics, broken hands; for dialogue over external audio — `Sync 3` / `OmniHuman 2.0` / `Seedance 2.5 Audio-Ref`. | **€10–€35** |
| **6. Infographics & branding** | **Programmatic (Remotion / Manim / FFmpeg):** clean HUD, prices (€999, €2,999), `CLARYEL` logo, `claryel.com` URL | Perfect typography, 0 text artifacts, instant localization (IT / EN / DE / FR / RU) from one JSON. | €0 |
| **7. Final polish** | One 3D LUT + light film grain (16mm/35mm, no oversharpening) + audio mixing (ducking −14 dB under speech, −14 LUFS). | Welds real footage, graphics and AI scenes into one expensive broadcast look. | €0 |

### 4.3 Matrix of ready commercial formats for `CLARYEL` (on real site facts)

1. **Format A — 15 s (performance / Reels / Shorts / X): "The Cloud & Server-Room Trap"** (on the `@uctive` / MixAI thesis)
   - `0:00–0:03` (hook): close-up of a real office — a manager looks at a cloud-AI bill and a data-leak warning. HUD title: *"CLOUD AI: Data leaves your office"*.
   - `0:03–0:06`: dark corner with a loud bulky rack and cable mess. Title: *"DIY LOCAL: €15k, noise, zero mobility"*.
   - `0:06–0:12`: bright desk with the real compact `CLARYEL Box`. A living entrepreneur asks by voice from a smartphone on the move. HUD: *"MIX AI: Private locally • Filtered cloud on demand"*.
   - `0:12–0:15`: packshot + offer: *"CLARYEL Box from €999 (VAT incl.) • Book architecture call €81.15 + VAT → claryel.com"*.
2. **Format B — 30 s (main B2B spot for site, LinkedIn, X, YouTube pre-roll): "Voice audit in 10 seconds"**
   - Built on the **real case from `claryel.com/software/`**: a business owner in a car or office asks by voice: *"How much did we spend on IT this year?"* → the HUD shows the system's real finding (€54,691 → fake invoices and duplicates found → human confirmation → cleaned to 188 valid invoices / €36,993.58 with backup copy).
   - Punchy trust accents: *"Data never leaves the office. Egress filter to cloud. Emergency encryption button. Ready out of the box from €999."*
3. **Format C — 60–90 s (image/engineering proof film for decision-makers):**
   - Honest `@uctive`-style anti-hype delivery: *"We moved our own business onto the DDR4 system we sell for €999. First test your model free in the cloud — and buy your Box only when you see the real saving."* Demonstrates the 3 levels (€999 / €2,999 / from €7,000), 24/7 support (Basic €0 → Individual) and a separate `CLARYEL Solar` teaser.

---

## 5. Track 2: MP3-to-music-video pipeline (from 4.9/10 to 10/10)

To get a clip that **does not read as "neural"** and holds the viewer for all 3–4 minutes, the pipeline must move from *"1 model, 32 similar prompts"* to a 7-stage studio architecture.

### 5.1 The 7-stage `MusicVideoFactory V2` architecture

#### Stage 1. Automatic musical decomposition (Audio-First)
The agent never cuts the clip "by eye at 10–15 seconds". `analyze_track.py` extracts:
1. **4-stem separation (`BS-RoFormer` / `Demucs v4`):** `vocals_dry.wav`, `drums.wav`, `bass.wav`, `other.wav`.
2. **Rhythm grid (`librosa` / `madmom`):** exact BPM, timestamp of every bar (`downbeats`), energy curve (`RMS` / spectral flux) to locate drops, pockets and transitions precisely.
3. **Phoneme-level vocal alignment (`WhisperX` on `vocals_dry.wav`):** timing of every line and word to ±20 ms.
4. **`edl_master.json` generation:** every shot length is an exact multiple of bars (e.g. 2–4 bars = 3.5–7.5 s in calm parts, 1–2 bars = 1.8–3.8 s on drops!). **Ban on shots longer than 8 seconds** — it is exactly the long 10–16 s shots that produced the freeze and monotony.

#### Stage 2. Director's Bible (the neuro-slop killer)
Before any frame generation, a rigid `style_bible.json`:
- **3-act story with action (not "standing and smiling"):** each act has a concrete goal/movement through space (e.g. searching for each other in the city → the journey → the meeting → dance/catharsis → quiet morning).
- **Monotonic Lighting Timeline:** strict ban on jumping backwards in time of day. Every shot gets a target color temperature (Kelvin) and exposure (sunset 3200K → dusk 5500K → night 7000K + practical lamps → dawn 6000K).
- **Mandatory shot-size alternation (shot rhythm):** Wide Establishing → Medium Action → Detail/Insert (hands, water, headlight, guitar) → Close-Up. Never 5 identical medium "two people centered" shots in a row.
- **AI-slop blacklist (negative visual bible):** ban on literal neon sticks/lasers out of water, on the painted Milky Way, on synchronized smiles into camera. Casting with living texture (light asymmetry, natural pores, matte skin without oily specular, light from real sources — street lamps, windows, headlights, the moon).

#### Stage 3. Keyframe-first storyboard + animatic (mandatory Human Gate #1)
- For each of the 40–55 shots in `edl_master.json`, generate the **Start Keyframe** (and where needed the **End Keyframe**) rigidly tied to a 3–4-angle **character sheet** (face front, 3/4, profile, full body).
- All still frames are assembled in ~30 seconds into `animatic_preview.mp4` over the original MP3.
- **A human watches the 4-minute animatic and discards in 5 minutes:** the time-of-day break, face drift, glossy skin, cheap backgrounds and boring rhythm — **before** any GPU hour or API credit is spent.

#### Stage 4. Hybrid shot routing (MixAI Video Router)
Every approved shot is automatically routed to the engine that makes that shot type at 10/10:
- **Route A — vocal close-ups (20–25% of runtime, strict lipsync):**
  - Input: **only the cleaned `vocals_dry.wav` stem** (cut exactly to the shot) + the approved Start Keyframe.
  - *Cloud reference (recommended for 10/10):* **`OmniHuman 2.0`** (best articulation of singing, held vowels and body mime from a single frame) or **`Seedance 2.5 Audio-Ref`** (up to 4K, 30 references). If the mouth must be fixed on an already-moving shot — **`Sync 3`**.
  - *Local reserve (€0):* **`LiveAvatar`** (Apache 2.0, distilled to 4 steps) or **`Wan2.2-S2V` / `LatentSync 1.6`** (512×512, 18 GB VRAM), strictly on `vocals_dry.wav` and short 3–5 s phrases.
- **Route B — atmospheric, landscape and simple shots (50–60% of runtime):**
  - **Locally on M5 Max (`LTX-2.5`) or RTX 5090 (`pi-H3`, 4 steps):** tied to **First + Last Keyframe** (excludes composition drift and guarantees arrival at the exact next edit point). Saves 60% of the budget!
- **Route C — complex physics (dances, hands, splashes, fast camera orbit, 15–20% of runtime):**
  - **Cloud via API:** **`Kling 4.0`** (best following of complex camera trajectory and body motion at an accessible price) or **`Seedance 2.5` / `Veo 3.1`**.

#### Stage 5. Multi-level QC Gate V2 (fixing Goodhart's law)
Every generated shot passes 5 automatic checks (on failure: auto-regeneration with another seed or escalation from local Route B to cloud Route C):
1. **Edge-trim guard (`scdet`):** check the first and last 1.0 s for morphing/artifacts; automatic trim + generate all clips with a **+1.5 s margin** (so the video is **never stretched** via `setpts` into "stickiness").
2. **Motion floor check (anti-freeze for the 03:52–04:03 class):** mean optical-flow magnitude M̄; if any 2-second window has M̄ below the minimum threshold (the frame "died"), the shot is rejected.
3. **Identity lock score (ArcFace / InsightFace):** cosine similarity of the face embedding at frames t ∈ {0.1T, 0.5T, 0.9T} vs the character-sheet reference must be **≥ 0.65**.
4. **Lighting & time-of-day continuity check:** median luma L* and color temperature vs the shot's target range from the `Lighting Timeline` — automatically catches 02:10→02:12-class breaks (night→day).
5. **Vocal lip-sync gate (Route A only):** `SyncNet` metrics (`LSE-D`, `LSE-C`) strictly against `vocals_dry.wav` + VLM check (`Qwen2.5-VL` / `Gemini Vision`) over a checklist of 6 binary flags: *no wax/oily skin, no hand/finger artifacts, no foreign light "rods" or text, natural mouth mime*.

#### Stage 6. Unified optical finish (the "AI patchwork" killer)
- Selective diffusion upscale/restoration of only the soft or local shots via local **`SeedVR2`** in ComfyUI (`batch_size ≥ 5`, `temporal_overlap` 4–8 frames, pilot test on one 5-second close-up first) or cloud **`Topaz Astra Creative / Starlight`**.
- **Unified grading (Color Bible):** every shot (local AND cloud) passes through **one shared 3D LUT** (`.cube`, film emulation with highlight control that cuts the digital "oily" skin sheen), light halation, and **real scanned 35 mm grain** overlay (FFmpeg/DaVinci). This visually welds different models into one camera.

#### Stage 7. Beat-locked mastering
- All cuts are locked to the `downbeats` grid from `edl_master.json` (±1 frame at 24 fps).
- **Hard cuts in 90%** of the clip — like real cinema and music videos; a crossfade is allowed only on smooth atmospheric landscapes (**crossfades on close-up faces banned**).
- The output master matches the full MP3 length exactly (down to the fading last second, **no `-shortest` truncation**).

---

## 6. Economics and time forecast (V1 vs V2)

| Metric | V1 (this repo, 100% local) | V2 hybrid (music video, 4:10) | V2 hybrid (CLARYEL commercial, 30 s) |
| :--- | :--- | :--- | :--- |
| **Total production time** | ~32–37 hours (incl. phase 0) | **3–5 hours** (incl. the animatic human gate) | **45–90 minutes** |
| **Electricity / API cost** | €0.45 (electricity) | **€25–€65** (API only for the 35–40% hero/vocal shots; the rest local €0) | **€10–€35** (API for 6–10 hero shots + TTS; graphics and drafts local €0) |
| **Load on the primary business brain (P2005)** | Basalt had to be parked in phase 0 | **0% downtime** (local render on M5 Max, P2005 untouched) | **0% downtime** |
| **Target score (20 parameters)** | **4.9 / 10** (actual) | **8.8–9.6 / 10** (industrial level) | **9.0–9.8 / 10** (conversion B2B level) |

---

## 7. Ready technical spec for the Hermes agent (migration to V2)

A structured specification that can be handed directly to an agent to build a new `video-factory-v2` repository/branch:

```yaml
project: claryel-video-factory-v2
architecture: hybrid-mixai # Sole local worker = M5 Max (drafts, B-roll, QC, grading); Cloud APIs for hero & singing vocal shots
hardware_allocation:
  # Operator directive: the NVIDIA box is permanently EXCLUDED from the video-factory
  # pool and must never be powered off or interrupted. It is only the business LLM brain.
  nvidia_rtx5090_24gb: "NOT a render worker: primary LLM brain (Basalt/Strata) only. Never interrupted, never powered down, never scheduled for video work."
  mac_m5_max_128gb: "Sole local worker, runs the whole local pipeline SEQUENTIALLY (one GPU stage at a time): Audio stems (BS-RoFormer/Demucs), BPM grid, WhisperX phonemes, LTX-2.5 drafts/B-roll, local lip-sync fallback, SeedVR2 upscale, Qwen2.5-VL QC, FFmpeg/Remotion mastering, LUT/grain, loudness"
  spare_box_on_request: "If the local lip-sync fallback or SeedVR2 proves impractical on Apple Silicon, ask the operator for a spare Linux+NVIDIA machine instead of touching the brain box."

tracks:
  commercial_claryel:
    durations_sec: [15, 30, 60, 90]
    rules:
      - "Audio-first: generate/approve final voiceover (IT/EN/RU) BEFORE any video generation"
      - "Real-assets priority: composite real CLARYEL Box photos + real ERP screen captures"
      - "ZERO text generated inside diffusion video models; ALL HUD/prices/logos rendered programmatically (Remotion/Manim/FFmpeg alpha)"
      - "Casting: authentic 32-52yo European SMB owners/specialists, matte skin, practical lighting, NO fashion-model slop"
      - "Fact-lock: pull exact prices (€999 / €2,999 / from €7,000, consultation €81.15+VAT, plans €0/€29.99/€149.99/from €500) ONLY from claryel.com JSON spec"

  music_video_mp3:
    pipeline_stages:
      1_audio_decompose:
        tools: ["demucs / bs-roformer", "librosa / madmom", "whisperx"]
        outputs: ["vocals_dry.wav", "instrumental.wav", "edl_master.json"]
        constraints:
          shot_duration_sec: [2.0, 7.5] # Hard cap <= 8s, beat-locked to downbeats
          extra_handle_sec: 1.5 # Generate +1.5s margin for clean edge trimming without setpts stretching
      2_director_bible:
        outputs: ["style_bible.json", "lighting_timeline.json", "character_sheet/"]
        constraints:
          monotonic_lighting: true # Strict prohibition of backwards time-of-day jumps
          slop_ban_list: ["floating neon sticks", "laser beams in ocean", "giant milky way stickers", "oily specular forehead", "synchronized stare-and-smile"]
      3_keyframe_animatic_gate:
        mandatory_human_approval: true
        output: "animatic_preview.mp4"
      4_mixai_shot_router:
        route_A_vocal_closeup:
          audio_input: "vocals_dry.wav (isolated stem ONLY)"
          primary_cloud: ["OmniHuman-2.0", "Seedance-2.5-A2V", "Sync-3"]
          # CUDA-only fallbacks: UNAVAILABLE while the sole local worker is Apple Silicon.
          # Route A then ships 100% via the cloud engines, or the operator attaches a spare Linux+NVIDIA box.
          fallback_local: ["LiveAvatar-4step", "Wan2.2-S2V", "LatentSync-1.6"]
          fallback_local_requires: "Linux + NVIDIA (MPS port not viable at 18 GB weights); disabled by default"
        route_B_atmosphere_broll:
          primary_local: ["LTX-2.5 (First+Last frame lock)"]
          secondary_local: ["pi-H3 (4 steps)"] # only if a spare NVIDIA box is attached
        route_C_complex_motion:
          primary_cloud: ["Kling-4.0", "Seedance-2.5", "Veo-3.1"]
      5_qc_gate_v2:
        checks:
          - "scdet_edge_trim: trim first/last morph frames using +1.5s handles"
          - "optical_flow_floor: reject any 2s window with near-zero motion"
          - "arcface_identity_cosine >= 0.65"
          - "lighting_timeline_delta_ok (Lab L* and color temp within shot target)"
          - "syncnet_lse_check (route_A vocal shots only)"
          - "vlm_slop_audit (Qwen2.5-VL / Gemini: skin matte, hands/wrists anatomy, zero synthetic background artifacts)"
      6_optical_unification:
        upscaler: "SeedVR2 (ComfyUI, batch_size>=5, temporal_overlap=6) or Topaz Starlight on soft shots only"
        grading: "Single unified 3D LUT (.cube) + subtle halation + real 35mm grain overlay across 100% of shots"
      7_beat_locked_master:
        transitions: "Hard cuts on downbeats (90%+); NO crossfades on close-up faces"
        audio_sync: "Exact full-length MP3 match, -14 LUFS loudness normalization"
```

---

## 8. How this document was published to GitHub

The source document noted that an AI chat has no direct write (`git push`) access to third-party GitHub repos and that passing a personal access token into a chat is unsafe (it would violate the project's own `secret-scanned-publication` procedure). Its recommended safe route — save the file into the local clone as `docs/POSTMORTEM_AND_V2_ARCHITECTURE.md`, run it through the standing `gitleaks` gate, commit and push via the Hermes agent — is exactly what was done: the owner delivered the file to the agent, the agent translated it to English (repo language policy), applied the standing secret gate (14-pattern grep + gitleaks) and the zero-Cyrillic sweep, then committed and pushed to `main`.
