#!/usr/bin/env python3
"""Clip pipeline per MASTER_SPEC.md: audio (Demucs) -> keyframes (16:9 crop + de-gloss) -> manifest.json."""
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np

FPS = 24
STYLE = ("natural soft satin skin texture, subtle cinematic sunset rim light, matte-satin editorial makeup, "
         "realistic fine skin details, shot on 35mm cinema lens, Arri Alexa color science")
NEGATIVE = ("greasy skin, sweaty face, oily highlights, plastic skin, enlarged pores, stretched aspect ratio, "
            "squashed face, distorted mouth, extra fingers, neon outline artifacts, morphing teeth")

SCENES = [
    {"id": 1,  "src_sec": 2.0,   "frames": 169, "lip_sync": False, "prompt": "Cinematic medium shot of a handsome bearded man in a black linen shirt and a brunette woman in a champagne silk slip dress facing each other in profile on a rocky beach at golden sunset, warm sunlight reflecting on calm sea waves, gentle breeze in hair"},
    {"id": 2,  "src_sec": 10.0,  "frames": 193, "lip_sync": False, "prompt": "Slow cinematic push-in on the couple standing in profile by the calm ocean at sunset, soft warm smiles, glowing golden horizon, natural skin tones, realistic hair movement in sea breeze, 35mm anamorphic lens"},
    {"id": 3,  "src_sec": 18.0,  "frames": 169, "lip_sync": False, "prompt": "Wide romantic shot on a wooden pier with a thatched gazebo at golden sunset, brunette woman in a backless champagne silk slip dress standing in three-quarter back view facing the bearded man in a black shirt, rich orange sky over calm water, cinematic lighting"},
    {"id": 4,  "src_sec": 24.0,  "frames": 145, "lip_sync": False, "prompt": "Medium shot on the wooden pier at sunset, golden sun path shimmering on the ocean between the woman in champagne silk dress and the man in black linen shirt, soft wind blowing long wavy brunette hair, filmic color grading"},
    {"id": 5,  "src_sec": 32.0,  "frames": 169, "lip_sync": False, "prompt": "Cinematic widescreen close-up portrait of a gorgeous brunette woman at golden sunset, soft velvet matte-satin skin texture without oily shine, warm sunset rim light on hair and shoulders, serene gentle smile, shallow depth of field, 85mm cinema lens"},
    {"id": 6,  "src_sec": 38.0,  "frames": 193, "lip_sync": False, "prompt": "Two-shot close-up in profile at sunset, brunette woman looking toward the glowing sun over the ocean with clean natural satin skin, handsome bearded man softly smiling behind her, warm golden hour glow, 35mm cinema film"},
    {"id": 7,  "src_sec": 46.0,  "frames": 169, "lip_sync": False, "prompt": "Blue hour twilight walk along the sandy shoreline beside a white illuminated wooden pier with warm lanterns, woman in champagne silk dress and bearded man in black shirt walking side by side, pastel pink and deep blue sky reflections on water"},
    {"id": 8,  "src_sec": 52.0,  "frames": 145, "lip_sync": False, "prompt": "Medium tracking shot during blue hour on the beach, woman in champagne silk dress turns her head toward the bearded man in black shirt, warm pier lights reflecting on silk fabric, soft natural skin, cinematic mood"},
    {"id": 9,  "src_sec": 56.5,  "frames": 145, "lip_sync": True,  "prompt": "Widescreen medium close-up of the brunette woman turning toward the camera on a waterfront promenade at night, colorful city skyline bokeh behind her, singing softly with natural lip movement, smooth satin skin texture, 50mm cinema lens"},
    {"id": 10, "src_sec": 64.0,  "frames": 169, "lip_sync": False, "prompt": "Over-the-shoulder shot from behind the brunette woman in a champagne silk dress walking toward the bearded man in a black shirt along a coastal promenade at night, vibrant city lights reflecting in the bay"},
    {"id": 11, "src_sec": 74.0,  "frames": 169, "lip_sync": True,  "prompt": "Close-up of the brunette woman singing emotionally with natural lip sync beside warm string fairy lights at dusk, bearded man looking at her in profile, soft diffused warm lighting, smooth matte-satin skin without sweat or glare"},
    {"id": 12, "src_sec": 80.0,  "frames": 217, "lip_sync": True,  "prompt": "Intimate close-up portrait with warm bokeh fairy lights in background, brunette woman singing and smiling warmly toward camera then glancing at the bearded man beside her, natural teeth and clean soft skin texture"},
    {"id": 13, "src_sec": 88.0,  "frames": 169, "lip_sync": False, "prompt": "Medium shot on a seaside terrace at night framed by a glowing cyan and warm amber neon ring arch, couple holding hands and laughing joyfully, string lights in background, cinematic night photography"},
    {"id": 14, "src_sec": 94.0,  "frames": 145, "lip_sync": False, "prompt": "Romantic dance under the glowing cyan and amber neon arch by the sea at night, bearded man raises his hand as the brunette woman spins gracefully in her champagne silk dress, natural hand anatomy, smooth motion"},
    {"id": 15, "src_sec": 102.0, "frames": 145, "lip_sync": False, "prompt": "Cinematic low-angle shot of the couple's bare feet standing in shallow ocean waves at twilight, colorful cyan and pink neon lights reflecting on wet sand and rippling water, gentle sea foam"},
    {"id": 16, "src_sec": 108.0, "frames": 169, "lip_sync": False, "prompt": "Medium shot on the beach at dusk, brunette woman twirling gracefully holding the hem of her flowing champagne silk dress beside the man in black shirt, soft out-of-focus neon bokeh in background, realistic silk physics"},
    {"id": 17, "src_sec": 116.0, "frames": 193, "lip_sync": True,  "prompt": "Medium shot aboard a luxury white motor yacht at night with subtle turquoise deck lighting, bearded man in black linen shirt singing a line while looking at the brunette woman in champagne silk dress, deep blue sea behind"},
    {"id": 18, "src_sec": 124.0, "frames": 241, "lip_sync": True,  "prompt": "Medium close-up on the yacht deck at night with glowing city skyline reflections on the water, brunette woman singing expressively while looking at the bearded man, soft moonlight and city glow on clean satin skin"},
    {"id": 19, "src_sec": 134.0, "frames": 193, "lip_sync": False, "prompt": "Wide cinematic shot of the couple standing side by side on a sleek motorboat cruising across the bay at dusk, illuminated city skyline behind them, wind gently blowing hair and silk dress"},
    {"id": 20, "src_sec": 140.0, "frames": 169, "lip_sync": False, "prompt": "Medium close-up on the boat at twilight, bearded man closes his eyes enjoying the sea breeze while the brunette woman looks toward the horizon, soft natural twilight tones, 50mm lens"},
    {"id": 21, "src_sec": 148.0, "frames": 265, "lip_sync": False, "prompt": "Smooth cinematic macro push-in on the brunette woman's expressive hazel-brown eyes at sunset, delicate natural freckles, soft velvet skin texture without oily shine, warm golden reflection in eyes, 100mm macro cinema lens"},
    {"id": 22, "src_sec": 160.0, "frames": 241, "lip_sync": True,  "prompt": "Intimate profile close-up on the beach at sunset, couple standing forehead to forehead holding hands, brunette woman softly singing with subtle natural lip movement, pastel sunset sky over calm sea"},
    {"id": 23, "src_sec": 170.0, "frames": 241, "lip_sync": True,  "prompt": "Medium close-up on a moonlit beach at night with soft silver backlight, brunette woman singing directly to the camera with accurate lip sync, bearded man standing beside her looking into camera, smooth soft-lit skin"},
    {"id": 24, "src_sec": 180.0, "frames": 193, "lip_sync": True,  "prompt": "Medium shot on a dimly lit pier at night, brunette woman dancing with arms raised gracefully while singing the chorus, bearded man holding her waist and watching her admiringly, clean natural lighting"},
    {"id": 25, "src_sec": 186.0, "frames": 193, "lip_sync": True,  "prompt": "Medium shot on the night beach with diagonal pink and cyan laser light beams in the sky behind the couple, brunette woman singing the chorus facing the bearded man, atmospheric concert-like haze"},
    {"id": 26, "src_sec": 194.0, "frames": 193, "lip_sync": True,  "prompt": "Close-up two-shot with soft pink and cyan light streaks in the background, couple gazing into each other's eyes then turning to look at the camera as the brunette woman sings, natural skin and hair detail"},
    {"id": 27, "src_sec": 204.0, "frames": 193, "lip_sync": True,  "prompt": "Wide medium shot on the shoreline at golden sunset, brunette woman walking through shallow surf swirling her champagne silk dress while singing, bearded man watching her with a warm smile, golden sun reflection on water"},
    {"id": 28, "src_sec": 212.0, "frames": 193, "lip_sync": True,  "prompt": "Dynamic medium shot of the couple spinning and dancing in shallow ocean water at golden hour, backlit water splashes sparkling in sunlight, joyful singing and laughter, high shutter speed film look"},
    {"id": 29, "src_sec": 220.0, "frames": 241, "lip_sync": True,  "prompt": "Joyful close-up of the couple laughing and singing together at night with colorful circular neon bokeh lights behind them, natural radiant matte-satin skin without harsh glare, genuine smiles"},
    {"id": 30, "src_sec": 230.0, "frames": 193, "lip_sync": False, "prompt": "Romantic medium shot on the beach under a clear starry night sky and glowing Milky Way galaxy over the ocean, couple embracing and turning toward the camera, soft starlight"},
    {"id": 31, "src_sec": 238.0, "frames": 241, "lip_sync": False, "prompt": "Medium shot of the couple sitting side by side on the edge of a weathered wooden pier at twilight, colorful neon reflections shimmering on the water behind them, clean edges without artificial outlines, calm intimate mood"},
    {"id": 32, "src_sec": 248.0, "frames": 241, "lip_sync": False, "prompt": "Final intimate profile close-up on the beach at pastel dawn, couple standing nose to nose with eyes closed in peaceful affection, soft ocean horizon behind them, gentle fade to black"},
]

def run(cmd):
    print(">>", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True)

def reduce_skin_glare(img_bgr):
    """Soft suppression of greasy highlights (highlights compression) without flattening geometry."""
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)
    mask = np.clip((L - 200.0) / 55.0, 0.0, 1.0)
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    L_clean = L - mask * 28.0
    merged = cv2.merge([np.clip(L_clean, 0, 255), A, B]).astype(np.uint8)
    result = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return cv2.bilateralFilter(result, d=5, sigmaColor=25, sigmaSpace=25)

def to_16x9(frame):
    """Crop to 1280x720 without distortion: scale by height + center crop by width."""
    h, w = frame.shape[:2]
    scale = 720.0 / h
    rw = int(round(w * scale))
    resized = cv2.resize(frame, (rw, 720), interpolation=cv2.INTER_LANCZOS4)
    x0 = (rw - 1280) // 2
    return resized[:, x0:x0 + 1280]

def main():
    src_video = Path("input/source_clip.mp4")
    if not src_video.exists():
        raise FileNotFoundError("Put the source clip at clip_project/input/source_clip.mp4")

    # 1. Uncompressed audio 44.1 kHz
    full_wav = Path("audio/full_mix.wav")
    if not full_wav.exists():
        run(["ffmpeg", "-y", "-i", str(src_video), "-vn", "-acodec", "pcm_s16le",
             "-ar", "44100", "-ac", "2", str(full_wav)])

    # 2. Clean vocals via Demucs htdemucs_ft
    vocals_wav = Path("audio/stems/htdemucs_ft/full_mix/vocals.wav")
    if not vocals_wav.exists():
        run(["demucs", "-n", "htdemucs_ft", "--two-stems=vocals", "-o", "audio/stems", str(full_wav)])

    # 3. Keyframes (16:9 crop without flattening + de-gloss) + vocal cutting at 24fps
    cap = cv2.VideoCapture(str(src_video))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    cursor_frame = 0
    manifest = []
    for sc in SCENES:
        sid = f"scene_{sc['id']:02d}"
        dur_sec = sc["frames"] / float(FPS)
        start_sec = cursor_frame / float(FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sc["src_sec"] * src_fps))
        ok, frame = cap.read()
        if ok:
            frame_16x9 = to_16x9(frame)
            cv2.imwrite(f"assets/keyframes_raw/{sid}.png", frame_16x9)
            cv2.imwrite(f"assets/keyframes_clean/{sid}.png", reduce_skin_glare(frame_16x9))
        clip_audio = Path(f"audio/clips/{sid}_vocals.wav")
        run(["ffmpeg", "-y", "-ss", f"{start_sec:.6f}", "-t", f"{dur_sec:.6f}",
             "-i", str(vocals_wav), "-acodec", "pcm_s16le", "-ar", "44100", str(clip_audio)])
        prompt = sc["prompt"] + (", mouth closed, serene romantic expression" if not sc["lip_sync"] else "") + ", " + STYLE
        manifest.append({
            "scene_id": sid,
            "start_sec": round(start_sec, 4),
            "duration_sec": round(dur_sec, 4),
            "num_frames": sc["frames"],
            "lip_sync": sc["lip_sync"],
            "keyframe_image": f"assets/keyframes_clean/{sid}.png",
            "vocals_audio": str(clip_audio) if sc["lip_sync"] else None,
            "prompt": prompt,
            "negative_prompt": NEGATIVE,
        })
        cursor_frame += sc["frames"]
    cap.release()
    Path("manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("scenes.json").write_text(json.dumps(SCENES, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done: {len(manifest)} scenes, duration {cursor_frame / FPS:.2f} s.")

if __name__ == "__main__":
    main()
