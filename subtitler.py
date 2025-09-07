import os
import tempfile
import subprocess
import whisper
from deep_translator import GoogleTranslator
import shutil

FFMPEG_PATH = "ffmpeg"  # faqat nomi, to‘liq yo‘l emas

def check_ffmpeg():
    if shutil.which(FFMPEG_PATH) is None:
        raise FileNotFoundError(
            "ffmpeg topilmadi! Onlayn serverlarda ffmpeg avtomatik o‘rnatilgan bo‘ladi. "
            "Agar lokal ishlatsangiz, ffmpeg ni PATH ga qo‘shing yoki serverda administratorga murojaat qiling."
        )
    return True

def set_ffmpeg_in_path():
    # Onlayn serverlarda kerak emas, lekin lokal uchun qoldirilgan
    pass

def generate_subtitles(video_path, progress_callback=None):
    if not check_ffmpeg():
        raise FileNotFoundError("ffmpeg topilmadi!")
    set_ffmpeg_in_path()
    audio_path = tempfile.mktemp(suffix=".wav")
    if progress_callback:
        progress_callback(5)
    subprocess.run([
        FFMPEG_PATH, "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if progress_callback:
        progress_callback(15)
    model = whisper.load_model("base")
    if progress_callback:
        progress_callback(20)
    result = model.transcribe(audio_path, fp16=False, verbose=False)
    segments = result["segments"]
    srt_path = tempfile.mktemp(suffix=".srt")
    total = len(segments)
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()
            f.write(f"{i+1}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")
            if progress_callback:
                p = 20 + int(75 * (i + 1) / total)
                progress_callback(p)
    os.remove(audio_path)
    if progress_callback:
        progress_callback(100)
    return srt_path

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def translate_subtitles(srt_path, dest_lang, progress_callback=None):
    out_path = tempfile.mktemp(suffix=f"_{dest_lang}.srt")
    with open(srt_path, "r", encoding="utf-8") as fin:
        lines = fin.readlines()
    blocks = []
    block = []
    for line in lines:
        if line.strip() == "":
            if len(block) == 3:
                blocks.append(block.copy())
            block = []
        else:
            block.append(line)
    if len(block) == 3:
        blocks.append(block.copy())
    total = len(blocks)
    with open(out_path, "w", encoding="utf-8") as fout:
        for i, block in enumerate(blocks):
            fout.write(block[0])
            fout.write(block[1])
            translated = GoogleTranslator(source='auto', target=dest_lang).translate(block[2])
            fout.write(translated + "\n\n")
            if progress_callback:
                p = int(100 * (i + 1) / total)
                progress_callback(p)
    if progress_callback:
        progress_callback(100)
    return out_path

def burn_subtitles(video_path, srt_path):
    out_path = tempfile.mktemp(suffix=".mp4")
    cmd = [
        FFMPEG_PATH, "-y", "-i", video_path, "-vf", f"subtitles={srt_path}", "-c:a", "copy", out_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path
    except Exception:
        return None
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path
    except Exception:
        return None
        return None
