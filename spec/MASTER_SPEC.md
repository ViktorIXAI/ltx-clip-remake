# MASTER SPEC — music video, 32 scenes, 04:13 (253.27 s)

(English translation of the working spec; original was authored in Russian.)

Source: `input/source_clip.mp4` (1696×768, 24 fps, 253.27 s, downloaded from X @uctive — the owner's own published clip).
Engine: LTX-2.5 (Lightricks/LTX-2 repository), Apple Silicon MPS.
Final: `renders/FINAL_MASTER.mp4` (1080p acceptable if time runs short), audio — single original track AAC 320 kbps.

## Global style

### Cast (appearance consistency)
- Heroine: slender brunette, long wavy dark-chestnut hair, expressive cheekbones, champagne silk slip dress on thin straps, small gold earrings.
- Hero: tall brunette with stubble (same length in every scene!), open black linen shirt, black trousers (dark shorts on the pier scene).

### Mandatory tail of every prompt
photorealistic skin with visible pores, matte skin, no sweat, no greasy shine; natural color grading, no neon outlines.

### Negative prompt (in every prompt)
cartoon, waxy skin, oily gloss, plastic face, extra fingers, distorted hands, neon outline, watermark, text.

## Frame math (LTX-2.5)
- Strictly 24 fps (1 frame = 41.6667 ms).
- Frame count only of the form 8k+1 (145, 169, 193, 217, 241, 265...).
- Scene audio is cut to exactly N/24.0 s from `vocals.wav` — zero drift by 04:13.

## Lip-sync
- `lip_sync: true` → LTX receives only the `vocals.wav` fragment (no drums/bass) + keyframe as the first frame.
- `lip_sync: false` → cast with closed mouth (`mouth closed, serene romantic expression`), no lip-sync audio conditioning.

## Draft defects to fix generatively
1. Flattened stub inserts (00:28, 01:26, 01:38–01:40, 01:52, 02:02, 02:10, 02:24–02:26, 02:36, 02:56, 03:28, 03:36, 03:46) — replaced by native 16:9 shots.
2. "Sweaty"/plastic skin and pores (00:32–00:42, 01:12–01:24, 02:28–02:34, 02:46–02:54, 03:38–03:44).
3. Chaotic lip-sync (mouth opens on instrumentals).
4. Inconsistent beard / neon outlines (01:50, 03:54).

## Storyboard (id | start in new clip | src_sec in source | frames | lip_sync)
01 | 00:00.0 | 2.0  | 169 | false — seashore, couple in profile, sunset, wind in hair
02 | 00:07.0 | 10.0 | 193 | false — camera push-in, smiles, sun below horizon
03 | 00:15.0 | 18.0 | 169 | false — pier with straw canopy, heroine back 3/4
04 | 00:22.0 | 24.0 | 145 | false — pier, angle change, curls in wind, sun glitter path
05 | 00:28.0 | 32.0 | 169 | false — close portrait of heroine (fix proportions/skin 00:28–00:32!)
06 | 00:35.0 | 38.0 | 193 | false — double profile portrait, remove forehead/cheek gloss
07 | 00:43.0 | 46.0 | 169 | false — dusk, walk by white lantern pier
08 | 00:50.0 | 52.0 | 145 | false — walk continues, head turn, lanterns on silk
09 | 00:56.0 | 56.5 | 145 | TRUE — night waterfront, skyscraper bokeh, first verse line
10 | 01:02.0 | 64.0 | 169 | false — meeting on night waterfront, city lights
11 | 01:09.0 | 74.0 | 169 | TRUE — close-up at garlands, singing, clean sweat-free skin
12 | 01:16.0 | 80.0 | 217 | TRUE — singing + smile to camera, gaze shifts to hero
13 | 01:25.0 | 88.0 | 169 | false — terrace with neon arch, laughing, holding hands
14 | 01:32.0 | 94.0 | 145 | false — dance under arch, heroine spins, hand anatomy!
15 | 01:38.0 | 102.0 | 145 | false — bare feet in a wave (replace stubs 01:38–01:40!)
16 | 01:44.0 | 108.0 | 169 | false — dance in water, wet silk, neon bokeh instead of scribbles 01:50
17 | 01:51.0 | 116.0 | 193 | TRUE — night yacht, turquoise light, hero sings along
18 | 01:59.0 | 124.0 | 241 | TRUE — yacht rail, night city, heroine sings
19 | 02:09.0 | 134.0 | 193 | false — boat across the bay, wide shot under canopy
20 | 02:17.0 | 140.0 | 169 | false — on the boat, breeze, eyes closed, hair in wind
21 | 02:24.0 | 148.0 | 265 | false — macro push-in on eyes (stubs 02:24–02:26, pores 02:30–02:34!); if engine rejects the length — split into 2×137
22 | 02:35.0 | 160.0 | 241 | TRUE — forehead-to-forehead at sunset, quiet singing
23 | 02:45.0 | 170.0 | 241 | TRUE — night beach, backlight, singing to camera
24 | 02:55.0 | 180.0 | 193 | TRUE — night pier, chorus starts, arms up (stub 02:56!)
25 | 03:03.0 | 186.0 | 193 | TRUE — beach, neon beams in sky, chorus
26 | 03:11.0 | 194.0 | 193 | TRUE — close two-shot, gazes at each other → to camera
27 | 03:19.0 | 204.0 | 193 | TRUE — golden sunset, walk along waterline, silk hem
28 | 03:27.0 | 212.0 | 193 | TRUE — dance in spray at sunset (stub 03:28!)
29 | 03:35.0 | 220.0 | 241 | TRUE — laughter and singing, neon circle bokeh (stub 03:36, gloss on cheek!)
30 | 03:45.0 | 230.0 | 193 | false — Milky Way, embrace on night shore (stub 03:46!)
31 | 03:53.0 | 238.0 | 241 | false — sitting on pier, clean neon reflection (outline artifact 03:54!)
32 | 04:03.0 | 248.0 | 241 | false — finale nose-to-nose at pastel dawn, fade to black

Frame sum: 6104 = 254.33 s ≈ song length (the ~1 s tail is trimmed when fitting the master track).

## Pipeline
1. `python scripts/run_pipeline.py`: full_mix.wav (44.1 kHz) → Demucs htdemucs_ft (--two-stems=vocals) → keyframes (1280×720 crop without flattening + reduce_skin_glare) → vocal cuts per 24 fps math.
2. Visual check of keyframes (scenes 05, 09, 15, 17, 18, 19, 21, 22, 24, 28, 29, 30): no flattened faces; if a frame lands on a transition, shift src_sec by ±0.5 s and re-run.
3. Render all scenes via LTX-2.5 (24 fps, 1280×720, upscale to 1080/4K optional): lip_sync scenes — keyframe + audio conditioning on vocals; the rest — image+prompt without audio conditioning.
4. ffmpeg concat strictly by manifest.json + overlay `audio/full_mix.wav` (AAC 320 kbps) → master.
