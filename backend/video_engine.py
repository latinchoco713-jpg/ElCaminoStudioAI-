import os
import random
import librosa
import numpy as np
from moviepy import *

def aplicar_estilo_cine(clip):
    return (
        clip
        .subclip(0, 2.5)
        .resize(height=720)
        .fadein(0.4)
        .fadeout(0.4)
        .resize(lambda t: 1 + 0.015 * t)
        .set_opacity(0.95)
    )

def estilo_triste_cinematico(clip):
    return (
        clip
        .subclip(0, 2.5)
        .resize(height=720)
        .fadein(0.6)
        .fadeout(0.6)
        .resize(lambda t: 1 + 0.01 * t)
        .set_opacity(0.90)
    )

def estilo_emocional(clip):
    return (
        clip
        .subclip(0, 2.5)
        .resize(height=720)
        .fadein(0.5)
        .fadeout(0.5)
        .resize(lambda t: 1 + 0.018 * t)
        .set_opacity(0.95)
    )

def estilo_intenso_cine(clip):
    return (
        clip
        .subclip(0, 2.5)
        .resize(height=720)
        .fadein(0.2)
        .fadeout(0.2)
        .resize(lambda t: 1 + 0.03 * t)
        .set_opacity(1.0)
    )

def obtener_beats(path):
    y, sr = librosa.load(path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    return beat_times

def obtener_energia_tempo(path):
    y, sr = librosa.load(path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    energia = np.mean(librosa.feature.rms(y=y))
    return energia, float(tempo)

def analizar_emocion(energia, tempo):
    if energia < 0.03 and tempo < 90:
        return "triste_cinematico"

    elif energia < 0.06:
        return "emocional"

    else:
        return "intenso_cine"

def seleccionar_estilo_audio(audio_path):
    energia, tempo = obtener_energia_tempo(audio_path)
    estilo = analizar_emocion(energia, tempo)
    return estilo, energia, tempo

def aplicar_estilo(clip, estilo):
    if estilo == "triste_cinematico":
        return estilo_triste_cinematico(clip)
    elif estilo == "emocional":
        return estilo_emocional(clip)
    elif estilo == "intenso_cine":
        return estilo_intenso_cine(clip)
    return aplicar_estilo_cine(clip)

def generar_video_con_beats(audio_path, clips_folder, beat_times, output_path, estilo=None):
    audio = AudioFileClip(audio_path)
    clips = []
    files = [f for f in os.listdir(clips_folder) if f.endswith(".mp4")]

    if len(files) == 0:
        raise Exception("No hay clips")

    if estilo is None:
        estilo, _, _ = seleccionar_estilo_audio(audio_path)

    i = 0
    for t in beat_times:
        clip_path = os.path.join(clips_folder, files[i % len(files)])
        clip = VideoFileClip(clip_path).subclip(0, 1.5)
        clip = aplicar_estilo(clip, estilo)
        clips.append(clip)
        i += 1

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

def create_video(music_path, clips_folder, estilo=None):
    if estilo is None:
        estilo, energia, tempo = seleccionar_estilo_audio(music_path)

    clips = []
    for file in os.listdir(clips_folder):
        if file.endswith(".mp4"):
            clip = VideoFileClip(os.path.join(clips_folder, file))
            clip = aplicar_estilo(clip, estilo)
            clips.append(clip)

    clips = sorted(clips, key=lambda x: x.duration)

    if clips:
        final_clip = concatenate_videoclips(clips, method="compose")

        if os.path.exists(music_path):
            audio = AudioFileClip(music_path).subclip(0, final_clip.duration)
            final_clip = final_clip.set_audio(audio)

        video_path = os.path.join('output', f'video_{random.randint(1000,9999)}.mp4')
        final_clip.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
        return video_path
    else:
        return None

def add_effects(video_path, effects):
    return video_path