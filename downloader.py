import yt_dlp
import os

DOWNLOAD_FOLDER = "downloads"

# Ensure folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# SAFE FORMAT MAP (does NOT trigger login restrictions)
VIDEO_QUALITY = {
    "144p": "18",   # mp4
    "240p": "18",
    "360p": "18",
    "480p": "135+140",
    "720p": "22",   # mp4
    "1080p": "137+140",
}

def download_video(url, quality="720p"):
    """Download video without merging restrictions."""
    
    format_id = VIDEO_QUALITY.get(quality, "22")

    ydl_opts = {
        "format": format_id,
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "noplaylist": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            return os.path.join(DOWNLOAD_FOLDER, ydl.prepare_filename(info))

    return None


def download_audio(url):
    """Download audio only (mp3)."""
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            return os.path.join(DOWNLOAD_FOLDER, filename)

    return None


def download_video_or_playlist(url, quality="720p", mode="video"):
    """Main function used by app.py"""

    # If playlist
    if "playlist" in url or "list=" in url:
        results = []
        ydl_opts = {
            "quiet": True,
            "ignoreerrors": True,
            "extract_flat": "in_playlist",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist = ydl.extract_info(url, download=False)

        if playlist and "entries" in playlist:
            for entry in playlist["entries"]:
                if not entry:
                    continue
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                if mode == "video":
                    results.append(download_video(video_url, quality))
                else:
                    results.append(download_audio(video_url))
        return results

    # Single Video
    if mode == "video":
        return [download_video(url, quality)]
    else:
        return [download_audio(url)]
