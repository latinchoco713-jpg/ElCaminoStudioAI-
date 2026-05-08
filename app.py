import shutil
import uuid
import os
import base64
from pathlib import Path

import librosa
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips, vfx
from openai import OpenAI

from backend.video_engine import generar_video_con_beats, obtener_beats


app = FastAPI(title="El Camino Studio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CLIPS_DIR = BASE_DIR / "assets" / "clips"
OUTPUT_DIR = BASE_DIR / "output"
SCENES_DIR = BASE_DIR / "scenes"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCENES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/www", StaticFiles(directory=str(BASE_DIR / "www"), html=True), name="www")


def obtener_energia_tempo(audio_path):

    y, sr = librosa.load(audio_path)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    energia = np.mean(librosa.feature.rms(y=y))

    # asegurar valores correctos
    tempo = float(np.array(tempo).item() if hasattr(tempo, "__len__") else tempo)
    energia = float(energia)

    return energia, tempo


def seleccionar_estilo_audio(audio_path):

    energia, tempo = obtener_energia_tempo(audio_path)

    if energia < 0.03:
        estilo = "calma"
    elif energia < 0.06:
        estilo = "emocional"
    else:
        estilo = "intenso"

    return estilo, energia, tempo


def analizar_audio(audio_path):
    energia, tempo = obtener_energia_tempo(audio_path)

    if energia < 0.03:
        mood = "dark cinematic rainy city"
    elif energia < 0.06:
        mood = "emotional sunset cinematic"
    else:
        mood = "intense storm futuristic city"

    return mood, energia, tempo


def generar_imagen(prompt, index):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY para generar imagenes con IA.")

    client = OpenAI(api_key=api_key)
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
    )

    image_bytes = base64.b64decode(response.data[0].b64_json)
    image_path = SCENES_DIR / f"img_{uuid.uuid4().hex}_{index}.png"
    image_path.write_bytes(image_bytes)

    return image_path


def crear_video_desde_imagenes(audio_path, images, output_path):
    audio = AudioFileClip(str(audio_path))
    clips = []

    for image in images:
        clip = ImageClip(str(image)).with_duration(2.5).resized(height=720)
        clip = clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])
        clips.append(clip)

    if not clips:
        raise RuntimeError("No hay imagenes para crear el video.")

    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    video.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac")

    audio.close()
    video.close()
    for clip in clips:
        clip.close()

    return output_path


def generar_video_con_ia(audio_path, output_path, scene_count=5):
    mood, energia, tempo = analizar_audio(audio_path)
    images = []

    for index in range(scene_count):
        prompt = f"{mood}, cinematic lighting, ultra realistic, film style"
        images.append(generar_imagen(prompt, index))

    crear_video_desde_imagenes(audio_path, images, output_path)

    return {
        "style": mood,
        "energy": energia,
        "tempo": tempo,
        "scenes": len(images),
    }


@app.get("/")
def health_check():
    return RedirectResponse(url="/www/index.html")


@app.post("/generate-video")
async def generate_video(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".mp3", ".wav", ".m4a", ".aac"}:
        raise HTTPException(status_code=400, detail="Sube un archivo de audio valido.")

    upload_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    output_name = f"video_{uuid.uuid4().hex}.mp4"
    output_path = OUTPUT_DIR / output_name

    try:
        upload_path.write_bytes(await file.read())

        try:
            metadata = generar_video_con_ia(str(upload_path), output_path)
            mode = "ai_images"
        except Exception as ai_error:
            estilo, energia, tempo = seleccionar_estilo_audio(str(upload_path))
            beat_times = obtener_beats(str(upload_path))

            if not CLIPS_DIR.exists() or not any(CLIPS_DIR.glob("*.mp4")):
                raise RuntimeError(
                    f"No se pudo usar IA ({ai_error}) y no hay clips MP4 en assets/clips."
                ) from ai_error

            generar_video_con_beats(
                audio_path=str(upload_path),
                clips_folder=str(CLIPS_DIR),
                beat_times=beat_times,
                output_path=str(output_path),
                estilo=estilo,
            )
            metadata = {
                "style": estilo,
                "energy": energia,
                "tempo": tempo,
                "beats": len(beat_times),
                "fallback_reason": str(ai_error),
            }
            mode = "local_clips"

        return {
            "status": "ok",
            "mode": mode,
            "video_url": f"/output/{output_name}",
            "video": f"/output/{output_name}",
            "video_path": str(output_path),
            **metadata,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo generar el video: {exc}") from exc
    finally:
        file.file.close()
