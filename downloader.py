import os
import io
import zipfile
import shutil

# ------------------------------
# AUDIO + VIDEO QUALITY OPTIONS
# ------------------------------

AUDIO_OPTIONS = {
    "60 kbps": "bestaudio[abr<=60]/bestaudio",
    "128 kbps": "bestaudio[abr<=128]/bestaudio",
    "192 kbps": "bestaudio[abr<=192]/bestaudio",
    "256 kbps": "bestaudio[abr<=256]/bestaudio",
    "320 kbps": "bestaudio[abr<=320]/bestaudio",
    "360 kbps": "bestaudio[abr<=360]/bestaudio",
}

VIDEO_OPTIONS = {
    "144p": "bestvideo[height<=144]+bestaudio/best",
    "240p": "bestvideo[height<=240]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "1440p (2K)": "bestvideo[height<=1440]+bestaudio/best",
    "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best",
    "Best": "bestvideo+bestaudio/best",
}


def download_video_or_playlist(
    url,
    download_path='downloads',
    download_type='video',
    quality='Best',
    content_type='Video',
    zip_output=False,
    zip_filename="downloaded_videos.zip"
):
    import yt_dlp  # safe import

    # ------------------------------
    # CLEAN FOLDER BEFORE DOWNLOAD
    # ------------------------------
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)

    # ------------------------------
    # FORMAT SELECTION
    # ------------------------------
    if download_type == "audio":
        ydl_format = AUDIO_OPTIONS.get(quality, "bestaudio")
    else:
        ydl_format = VIDEO_OPTIONS.get(quality, "best")

    is_playlist = (content_type == "Playlist")

    # ------------------------------
    # YT-DLP OPTIONS
    # ------------------------------
    ydl_opts = {
        "format": ydl_format,
        "ignoreerrors": True,
        "quiet": True,
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "noplaylist": not is_playlist,
        "extract_flat": False
    }

    # ------------------------------
    # APPLY MP3 POSTPROCESSOR
    # ------------------------------
    if download_type == "audio":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    # ------------------------------
    # DOWNLOAD
    # ------------------------------
    playlist_titles = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # If playlist → collect video titles
        if is_playlist and "entries" in info:
            playlist_titles = [e["title"] for e in info["entries"] if e]

    # ------------------------------
    # COLLECT DOWNLOADED FILES
    # ------------------------------
    downloaded_files = []
    for root, _, files in os.walk(download_path):
        for f in files:
            downloaded_files.append(os.path.join(root, f))

    # ------------------------------
    # ZIP OUTPUT
    # ------------------------------
    if zip_output:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for file in downloaded_files:
                z.write(file, os.path.basename(file))

        zip_buffer.seek(0)
        return zip_buffer, playlist_titles

    return downloaded_files, playlist_titles
