import yt_dlp
import os
import shutil

# ---------------------------------------------
# Clean folder before downloads
# ---------------------------------------------
def clean_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


# ---------------------------------------------
# DOWNLOAD SINGLE VIDEO (VIDEO ONLY)
# ---------------------------------------------
def download_video(url, quality, output_folder="output"):
    clean_folder(output_folder)

    # Map UI quality → yt-dlp format
    video_format_map = {
        "144p": "bestvideo[height=144]",
        "240p": "bestvideo[height=240]",
        "360p": "bestvideo[height=360]",
        "480p": "bestvideo[height=480]",
        "720p": "bestvideo[height=720]",
        "1080p": "bestvideo[height=1080]",
        "1440p (2K)": "bestvideo[height=1440]",
        "2160p (4K)": "bestvideo[height=2160]"
    }

    fmt = video_format_map.get(quality, "bestvideo")

    ydl_opts = {
        "format": fmt,       # VIDEO ONLY
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "merge_output_format": None,  # no merging at all
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename



# ---------------------------------------------
# DOWNLOAD AUDIO ONLY
# ---------------------------------------------
def download_audio(url, quality, output_folder="output"):
    clean_folder(output_folder)

    # Map UI → yt-dlp audio bitrates
    audio_quality_map = {
        "60kbps": "60",
        "128kbps": "128",
        "192kbps": "192",
        "256kbps": "256",
        "320kbps": "320",
        "360kbps": "360"
    }

    abr = audio_quality_map.get(quality, "128")

    ydl_opts = {
        "format": "bestaudio",        # AUDIO ONLY
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegAudioConvertor",
                "preferredcodec": "mp3",
                "preferredquality": abr
            }
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")



# ---------------------------------------------
# PLAYLIST DOWNLOAD (EACH ITEM SEPARATELY)
# ---------------------------------------------
def get_playlist_items(url):
    """Return playlist items (title + URL) without downloading."""
    ydl_opts = {"quiet": True, "extract_flat": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" not in info:
            return []

        items = []
        for entry in info["entries"]:
            if entry:
                items.append({
                    "title": entry.get("title"),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}"
                })

        return items

