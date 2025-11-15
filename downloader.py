import os
import yt_dlp
from io import BytesIO
import zipfile


# ---------------------------
#  VIDEO QUALITY MAP
# ---------------------------
VIDEO_FORMATS = {
    "240p": "bestvideo[height<=240]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "1440p (2K)": "bestvideo[height<=1440]+bestaudio/best",
    "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best",
}


# ---------------------------
#  AUDIO QUALITY MAP
# ---------------------------
AUDIO_FORMATS = {
    "60kbps": "bestaudio[abr<=60]",
    "128kbps": "bestaudio[abr<=128]",
    "192kbps": "bestaudio[abr<=192]",
    "256kbps": "bestaudio[abr<=256]",
    "320kbps": "bestaudio[abr<=320]",
    "360kbps": "bestaudio[abr<=360]",
}


# ----------------------------------------------------
#   EXTRACT PLAYLIST ITEMS (TITLE + URL)
# ----------------------------------------------------
def get_playlist_items(url):
    ydl_opts = {"quiet": True, "extract_flat": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)

    entries = data.get("entries", [])
    playlist = []

    for e in entries:
        playlist.append({
            "title": e.get("title", "No title"),
            "url": f"https://www.youtube.com/watch?v={e.get('id')}"
        })

    return playlist


# ----------------------------------------------------
#   DOWNLOAD SINGLE VIDEO
# ----------------------------------------------------
def download_video(url, quality):
    fmt = VIDEO_FORMATS.get(quality, "bestvideo+bestaudio")
    output = "output_video.%(ext)s"

    ydl_opts = {
        "format": fmt,
        "outtmpl": output,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find downloaded file
    for ext in ("mp4", "mkv", "webm"):
        if os.path.exists(f"output_video.{ext}"):
            return f"output_video.{ext}"

    return None


# ----------------------------------------------------
#   DOWNLOAD SINGLE AUDIO
# ----------------------------------------------------
def download_audio(url, quality):
    fmt = AUDIO_FORMATS.get(quality, "bestaudio")
    output = "output_audio.%(ext)s"

    ydl_opts = {
        "format": fmt,
        "outtmpl": output,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if os.path.exists("output_audio.mp3"):
        return "output_audio.mp3"

    return None
