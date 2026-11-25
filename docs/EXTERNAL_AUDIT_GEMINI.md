# External audit: Gemini review of the experiment and the V2 architecture

This document is an **external audit** produced by Google Gemini ("Gemini Neon") on 2026-11-25, pasted into the project chat by the owner and reproduced here in translation. It is published verbatim in substance: the defect map, the process postmortem, the two proposed production pipelines, and the V1-vs-V2 economics are the auditor's, not ours. Where our own measurements disagree with the auditor's claims we note it inline.

Transmission note: the source paste was truncated — section 7 (the ready-to-implement V2 spec) and section 8 (publishing instructions) were cut off mid-sentence and are marked below. Some glyph/number characters were lost in the paste; those spots are marked `[glyph lost in paste]`. **Update:** the complete document was later delivered as a file and is published, with all previously lost numbers restored, as the canonical `docs/POSTMORTEM_AND_V2_ARCHITECTURE.md`; this file is kept as the first-received copy.

---

## 1. Source verification and honest access boundaries (fact-check log)

What the auditor claims was confirmed by search, full video viewing, and notebook logs — and what it could not access directly.

**1.1 Confirmed origin thread on X (experiment starting point)**
- Chinese post by @pixelaigc, 21-22 November 2026: `https://x.com/pixelaigc/status/2124520344778313850` (linked repo: `https://github.com/pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow`).
- Facts from that post: local generation of a 30-second video **with audio** on an RTX 3060 12 GB (+24 GB RAM) using **pi-H3** — 2 steps, 480p, 1071 s (~17.85 min) — driven by a 7-block director prompt (dialogue after "Lust, Caution" / 《色戒》 with FACS facial codes).
- pi-H3 dating per the auditor: LakonLab blog announcement (Hansheng Chen et al.) 10-11 November 2026 (`hanshengchen.com/blog/pi-h3/`, `github.com/Lakonik/LakonLab`); public weights + ComfyUI nodes 21 November 2026. The CLARYEL experiment started the next day (22.11.2026, 21:00 CET).
  - *Our note: consistent with our own record — first Phase-0 session 22.11 21:09 CET; we dated the model itself from the weights release (21.11).*

**1.2 Confirmed facts about the CLARYEL business** (`claryel.com` / `claryelsolar.com`)
The auditor indexed the public site: legal entity CLARYEL S.R.L.S., Via Leonardo Da Vinci 26, 22073 Fino Mornasco (CO), Italy; VAT 04258140138; ATECO 62.10.00; participant in Bando Nuova Impresa 2026 (Regione Lombardia). Sales currently B2B (VAT/P.IVA holders) only. Product line (prices incl. VAT): Level 1 Local AI Start €999 (Xeon E5-2690 v4, 64 GB DDR4 ECC, Tesla P100 16 GB); Level 2 Local AI Business €2,999 (Core Ultra 7 270K Plus, 64 GB DDR5, RX 9070 16 GB, 2 TB PCIe 5.0 NVMe); Level 3 Local AI Pro from €7,000 (examples: Mac Studio M3 Ultra 256 GB, MacBook Pro M5 Max 128 GB) + storage/backup/UPS. Support: consultation €81.15+VAT; plans Basic €0 / Plus €29.99 / Pro €149.99 / Individual from €500 per month. MixAI philosophy: local-first, privacy-filtered optional cloud; voice-first operation; the public ERP-audit case (fake/duplicate invoices found by voice query, cleaned to 188 valid invoices with rollback history); emergency data-encryption button; free voice-managed website; Home Assistant integration; GDPR / CNIL / NIS2 / EU AI Act Art. 50 posture. The honest-engineer public voice (@uctive): DDR5→DDR4 switch thread (status/2122988375888040023, 18.11.2026), Strata-vs-Basalt 6-part benchmark on RTX 5090 Laptop (status/2123323827144814599, 19.11.2026), GPU price +33%/45 days monitoring, Docker-vs-KVM isolation audit pausing a deploy (09.11.2026), "test the model free in cloud before buying hardware" (08.11.2026), €135 garage AI-server experiment (12.11.2026).

**1.3 Access limits (stated honestly by the auditor)**
- Closed X timeline not directly parseable; `x.com/uctive/status/2124515830943641634` not indexed at audit time, so its thesis is taken from the owner's task statement and the confirmed `claryel.com/mixai/` article.
- The `ViktorIXAI/ltx-clip-remake` repo (published 25.11.2026 21:44 CET, ~1 h before the audit) was not yet search-indexed; the audit therefore relies on the commit-`58680eb` metrics and artifact list from the owner's report, the 22-25 November phase logs, and frame-level analysis of the attached 04:12 video.

---

## 2. Frame-by-frame audit of the final clip (04:12) — the 4.9/10 rating confirmed

The auditor watched the full video ("Neon Over the Water") and confirms the 4.9/10 score with a timecode defect map:

| Timecode | Defect class | What is on screen |
|---|---|---|
| 00:21 | Cut discontinuity / geometry drift | Pier, gazebo and lamppost orientation flips across the cut on the same sunset background |
| 00:28-00:34, 02:25-02:35, 03:36-03:45 | Plastic / oily skin (AI gloss) | Extreme close-ups (esp. macro eye/nose bridge at 02:25-02:35): forehead and cheek skin has unnatural wet-lacquer specular sheen; the matte formula did not remove the synthetic micro-shine |
| 00:54 | Local face artifact | Brief spot/defect on the man's forehead during a head turn |
| 00:56-01:01, 01:09-01:15 | Lipsync + appearance drift | At 00:58 the heroine's face visibly ages and the jawline changes; at 01:09 the mouth opens into a hypertrophied "O" not matching the sung syllables ("Let's have dance fight...") |
| 01:04-01:08, 02:10-02:12, 03:20-03:27 | Critical time-of-day logic break | The clip jumps back in time: deep-night city (01:03) crossfades back into bright sunset (01:05); night city on the boat deck (02:10) dissolves into bright daylight sunset inside the same scene (02:12); after night lasers (03:19) a hard revert to sunny golden beach (03:20) |
| 01:18-01:19, 01:27-01:30 | Crossfade mud + loop repeat | Double-exposure "ghosting" when dissolving large faces (01:18); a repeat loop of the kiss under the neon arch at 01:30 |
| 01:33-01:38, 03:28-03:35 | Sticky AI dance physics | Mechanical arm-waving, stiff gestures typical of diffusion video without a choreography reference |
| 01:45-01:51, 03:04-03:11 | Literal AI-slop in backgrounds | Word-literal rendering of "neon lights over the water": absurd glowing neon squiggles on poles sticking out of the sea (01:46); cheap pink-blue laser sheets firing vertically out of the water (03:04) |
| 02:00-02:09 | Hero identity drift | Against the night skyscraper the man's profile changes (different nose, different beard), then the two smile motionless at each other nose-to-nose for 7 s |
| 03:14-03:19 | Cliché "look at camera + wink" | Both characters turn in sync to the lens and freeze with glossy smiles |
| 03:46-04:03 | Anatomy break + cartoon background + frozen frame | A painted Milky Way with huge white snowflake dots in the sky; an unclear white glove/bandage morphing on the man's hand around her waist (03:47-03:50); from 03:52 to 04:03 (~11 s!) the frame is almost completely frozen, killing the finale |

**What genuinely worked (base to keep):**
- 00:00-00:14 (sunset prologue and kiss by the rocks), 01:39-01:44 (low angle of bare feet in water with reflections), 04:04-04:12 (pre-dawn forehead-to-forehead finale) look organic and cinematic.
- Costume consistency (champagne silk dress + open black shirt) held across 4+ minutes.
- Engineering discipline of the release: power telemetry (1,796 samples, 1.48 kWh, 0 throttling on M5 Max), reproducible code, clean Gitleaks-published record — described as exemplary engineering culture.

---

## 3. Deep process postmortem (22-25 November): what was done wrong

Three architectural switches in three days:
1. **Phase 0** (P2005 / RTX 5090 Laptop 24 GB + pi-H3): 22 scenes, 305.5 GPU-minutes (~5.1 h pure render). Found: no audio-to-video lip-sync, reference frame causes a jump at scene start, rendering forces parking the main business brain (Basalt) from 23,933 MiB to 266 MiB VRAM.
2. **Phase 0.5** (LatentSync → Wan2.2-S2V-14B): 3.1-3.3 GPU-min per second of footage, 53-57-frame (~2 s) windows, visuals of August-2025 generation.
3. **Phase 1** (MacBook Pro M5 Max 128 GB + LTX-2.5 22B): 32 scenes, 253.27 s, ~32 h from weight download to master, ~€0.45 electricity, automatic QC gates (MediaPipe, Qwen2.5-VL).

**Six systemic errors that turned 32+ hours into 4.9/10:**

1. **Local-purism trap** — a direct contradiction of the project's own MixAI philosophy (local for private data, drafts and unlimited iteration; cloud when the quality ceiling and cost-per-result matter). There was no trade secret in this clip, yet one local model (LTX-2.5) was loaded with everything: vocal lip-sync, choreography, macro skin, and a 4-minute storyline. Result: 32 hours of waiting and a 4.9/10 ceiling instead of a hybrid render of the ~25% problem scenes for €15-30.
2. **Wrong audio architecture** (root cause of the 4/10 lipsync). Feeding LTX-2.5 the *mixed* music track (trance beat + bass + reverb + vocal) makes it hallucinate abstract mouth motion — it cannot isolate phonemes through a dense mix (our own numbers cited: scene_22 corr 0.268, boost −0.261; corroborated by late-2026 community tests). Vocal shots need stem separation first (BS-RoFormer / Demucs → dry vocal) plus a dedicated performance engine.
   - *Our note: we did condition on a Demucs vocal stem — but a weak htdemucs_ft stem with reverb bleed behaved close to a mixed track on dense shots; the critique stands.*
3. **No Keyframe-First Animatic stage** (blind video generation). Launching 22-32 clips from text + two portraits inevitably produces face drift, time-of-day jumps and empty repeats. In professional 2026 AI production no video render starts before a storyboard of static Start/End keyframes is assembled into a slideshow animatic under the MP3. Fixing light, skin, stray neon poles and day/night at the *image* level takes 15 minutes, not 32 hours.
4. **Proxy-metric illusion in QC gates (Goodhart's law)**. The automatic gates (MediaPipe corr, skin-matte formula) honestly measured technical passability but were blind to the main neuro-slop triggers: unnatural smiles, the 11-second freeze (03:52-04:03), absurd neon rods in water (01:46), the white-glove artifact (03:48), night→day regressions (02:12, 03:20).
5. **"Literal illustration" direction and glossy casting**. "Beautiful 25-year-old European woman + 28-year-old man on a sunset beach" across 32 scenes guarantees an AI-postcard; the viewer is bored by second 90 — no dramatic action, no shot-size/rhythm variation, lyrics illustrated word-for-word.
6. **Assembly errors**: long crossfades on close-ups create dirty double exposure (01:18, 01:27); cuts not locked to the bar grid (BPM/downbeats) drain the electronic track's drive.

---

## 4. Direction 1: CLARYEL business commercial pipeline (10-90 s)

**Strategic rule for B2B.** The audience is Italian/European SMB owners with P.IVA considering €999-7,000+ hardware and €29.99-500/mo subscriptions. Main risk: glossy "cyberpunk AI" with model faces and painted neural-network servers creates instant distrust ("if even their ad is fake, what about their server?").

**The 10/10 formula — hybrid "Real + MixAI Commercial Pipeline":**
- ~40% of frames real (maximum trust): real photos/short shoots of the actual CLARYEL Box (Level 1/2/3), real voice-answer UI, real invoice-audit screen, clean programmatic vector graphics (Remotion / Manim / FFmpeg alpha overlay — total ban on generating text inside the video model).
- ~60% photorealistic AI scenes with ordinary living people: not photomodels but realistic European entrepreneurs 32-52 (light wrinkles, natural office light, ordinary clothes, Lombardy/Milan offices, car, workshop, solar farm for CLARYEL Solar).

**Optimal tool stack (MixAI for video, Nov 2026):**

| Stage | Tool (local vs cloud) | Why | Budget per 30 s |
|---|---|---|---|
| 1. Script + storyboard (EDL) | LLM (Claude/Gemini/local Qwen) | Hard 3-s hook, Pain→Contrast→Proof→Offer, shot timing 1.5-3.5 s | €0 |
| 2. Voiceover | ElevenLabs / Cartesia / local TTS (IT/EN/RU) | Crystal diction, exact line lengths *before* video render | ~€0.5-1 |
| 3. Approved start/end keyframes | Local Flux / Qwen-Image or cloud GPT-Image / Imagen + real CLARYEL Box photos | 100% control of photorealism, matte skin, light, the real product (img2img/compositing) before any video render | €0-2 |
| 4. Draft motion / animatic | Local: LTX-2.5 (M5 Max) or pi-H3 (RTX 5090) | Free rhythm/angle/duration check | €0 |
| 5. Final hero-shot render (MixAI) | Cloud API: Veo 3.1 (4-8 s, reference dialogue/cinematic realism), Seedance 2.5 (≤30 s, ≤30 refs, 4K, exact brief-following), Kling 4.0 (precise camera choreography, ~2.4× cheaper than Seedance at 1080p); for dialogue-on-external-audio: Sync 3 / OmniHuman 2.0 / Seedance 2.5 Audio-Ref | Removes plastic, sticky physics, broken hands with guarantee | €10-35 |
| 6. Infographics/branding | Programmatic (Remotion/Manim/FFmpeg) | Perfect type, 0 text artifacts, instant IT/EN/DE/FR/RU localization from one JSON | €0 |
| 7. Final polish | One 3D LUT + light film grain (16/35 mm, no oversharpen) + audio mix (ducking −14 dB under speech, −14 LUFS) | Welds real footage + graphics + AI scenes into one expensive look | €0 |

**Ready commercial formats from real site facts:**
- **A — 15 s (Reels/Shorts/X): "The Cloud & Serverroom Trap"** — hook: real office, manager staring at a cloud-AI bill + data-leak warning ("CLOUD AI: Data leaves your office"); dark corner with a noisy rack and cables ("DIY LOCAL: €15k, noise, zero mobility"); bright desk with the compact CLARYEL Box, entrepreneur asking by phone on the move ("MIX AI: Private locally • Filtered cloud on demand"); end card "CLARYEL Box from €999 (VAT incl.) • Book architecture call €81.15 + VAT → claryel.com".
- **B — 30 s (main B2B spot for site/LinkedIn/X/YouTube pre-roll): "Voice invoice audit in 10 seconds"** — built on the real published case: owner asks by voice "what did we spend on IT this year?" → HUD shows the real finding (€54,691 → fake invoices and duplicates found → human-confirmed cleanup → 188 valid invoices / €36,993.58 with backup/rollback). Trust accents: data never leaves the office, egress filter, emergency encryption button, from €999.
- **C — 60-90 s (engineering anti-hype proof film for decision-makers)** — honest @uctive voice: "we moved our own business onto the DDR4 machine we sell for €999; test your model free in the cloud first, buy the Box only when the savings are real". Shows the three levels, the support ladder, a CLARYEL Solar teaser.

---

## 5. Direction 2: MP3-to-music-video pipeline — how to get from 4.9/10 to 10/10

Move from "one model, 32 similar prompts" to a 7-stage studio architecture (**MusicVideoFactory V2**):

**Stage 1. Automatic musical decomposition (Audio-First).** Never cut the clip "by eye at 10-15 s". `analyze_track.py` extracts: (a) 4 stems via BS-RoFormer/Demucs v4 (`vocals_dry.wav`, drums, bass, other); (b) rhythm grid (librosa/madmom): exact BPM, per-bar downbeat timestamps, energy curve (RMS/spectral flux) to locate drops, pockets, transitions; (c) phoneme-level vocal alignment (WhisperX on `vocals_dry.wav`); (d) `edl_master.json` where every shot length is an integer number of bars (e.g. [glyph lost in paste] bars on calm parts, [glyph lost in paste] on drops) and **no shot longer than 8 s** — the 10-16 s shots are exactly what produced the freeze and monotony.

**Stage 2. Director's Bible (the neuro-slop killer).** A hard `style_bible.json` before any frame is generated: a 3-act story with real movement/goals (search → journey → meeting → dance/catharsis → quiet morning); a monotonic **Lighting Timeline** — a hard ban on jumping backwards in time of day, each shot gets a target color temperature and exposure (sunset → dusk → night + practicals → dawn); mandatory **shot-size alternation** (wide establishing → medium action → detail insert → close-up; never 5 identical mediums in a row); a **negative visual bible** banning literal neon rods/lasers from water, painted Milky Ways, synchronized smiles at camera, and casting with living texture (light asymmetry, real pores, matte skin without oily specular, light from real sources — streetlights, windows, headlights, moon).

**Stage 3. Keyframe-first storyboard + animatic (mandatory human gate #1).** For each of the 40-55 shots in `edl_master.json`, generate Start (optionally End) keyframes locked to a 3-4-angle character sheet (front, 3/4, profile, full body). Assemble all stills into `animatic_preview.mp4` over the original MP3 in ~30 s. A human watches the 4-minute animatic and kills — in 5 minutes — the time-of-day breaks, face drift, glossy skin, cheap backgrounds and boring rhythm *before* any GPU hour or API credit is spent.

**Stage 4. Hybrid shot routing (MixAI Video Router).** Each approved shot goes to the engine that makes that shot type at 10/10:
- **Route A — vocal close-ups (20-25% of runtime, strict lipsync):** input is the *dry vocal stem* cut exactly to the shot + approved start keyframe. Cloud reference for 10/10: **OmniHuman 2.0** (best singing articulation, held vowels, body mime from one frame) or **Seedance 2.5 Audio-Ref** (≤4K, 30 refs); fixing the mouth on an already-moving shot: **Sync 3**. Local fallback (€0): **LiveAvatar** (Apache-2.0, 4-step distilled) or **Wan2.2-S2V / LatentSync 1.6** ([glyph lost in paste], 18 GB VRAM) strictly on `vocals_dry.wav`, 3-5 s phrases.
- **Route B — atmospheric/landscape/simple shots (50-60%):** local LTX-2.5 on M5 Max or pi-H3 4-step on RTX 5090, conditioned on **first + last keyframe** (kills composition drift and guarantees arrival at the exact next edit point). This alone saves ~60% of the budget.
- **Route C — complex physics (dance, hands, splashes, fast camera orbits, 15-20%):** cloud API **Kling 4.0** (best complex camera/body following at accessible price) or Seedance 2.5 / Veo 3.1.

**Stage 5. Multi-level QC Gate V2 (fixing Goodhart).** Five automatic checks per shot (fail → regenerate with a new seed or escalate Route B → cloud Route C):
1. **Edge-trim guard (scdet):** check first/last [glyph lost in paste] for morphing, auto-trim; generate every clip with [glyph lost in paste] headroom so nothing is ever time-stretched with `setpts` (the "sticky" look).
2. **Motion floor check (anti-freeze):** mean optical-flow magnitude; if any 2-s window falls below [glyph lost in paste] the shot is dead → reject.
3. **Identity lock (ArcFace/InsightFace):** cosine similarity of face embeddings at sampled frames vs the character-sheet reference must be ≥ [glyph lost in paste].
4. **Lighting/time-of-day continuity:** median luma and color temperature vs the shot's target range — auto-catches the 02:10→02:12 (night→day) class.
5. **Vocal lipsync gate (Route A only):** SyncNet LSE-D/LSE-C strictly against `vocals_dry.wav`, plus a VLM pass (Qwen2.5-VL / Gemini Vision) over 6 binary flags: no wax/oily skin, no hand/finger artifacts, no foreign light-rods or text, natural mouth mime.

**Stage 6. One optical finish (the patchwork killer).** Selective diffusion upscale/restoration of only the soft shots via local **SeedVR2** in ComfyUI (batch [glyph lost in paste], temporal_overlap [glyph lost in paste] frames, 5-s close-up pilot first) or cloud Topaz Astra Creative / Starlight. Then **one grade for everything**: a single 3D LUT (.cube, film emulation with highlight rolloff that cuts the digital oily sheen), light halation, real scanned 35 mm grain overlay — visually welding different models into one camera.

**Stage 7. Beat-locked mastering.** All cuts snapped to the downbeat grid from `edl_master.json` (±[glyph lost in paste] frame at 24 fps). **Hard cuts in ~90%** of the clip — like real editing; crossfades only on gentle landscape shots, banned on faces. The output master matches the full MP3 length exactly, to the last fading second (no `-shortest` truncation).

---

## 6. Economics and time: V1 vs V2 (auditor's projection)

| Metric | V1 (this repo, 100% local) | V2 hybrid (music video, 4:10) | V2 hybrid (CLARYEL 30 s commercial) |
|---|---|---|---|
| Total production time | ~32-37 h (incl. phase 0) | 3-5 h (incl. the animatic human gate) | 45-90 min |
| Electricity / API cost | €0.45 electricity | €25-65 API (only 35-40% hero/vocal shots; rest local €0) | €10-35 API (6-10 hero shots + TTS) |
| Load on the business brain (P2005) | Basalt had to be parked in phase 0 | 0% downtime (local render on M5 Max) | 0% downtime |
| Target score (20 parameters) | 4.9/10 (actual) | 8.8-9.6/10 | 9.0-9.8/10 |

---

## 7. Ready technical spec for the Hermes agent (migration to V2)

*[Truncated in the transmitted message — the section announced a structured specification for a `video-factory-v2` repository/branch, but the body did not arrive. To be appended when the full text is re-sent.]*

## 8. How this document got into GitHub

*[Truncated in the transmitted message. Actual method used: the owner pasted the analysis into the Hermes agent chat; the agent translated, ran the publication secret gate, and committed it to this repository. No third-party token was involved.]*
