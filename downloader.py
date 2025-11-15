import os
import io
import zipfile
import shutil

VIDEO_OPTIONS = {
    "144p": "best[height<=144][ext=mp4]/best[height<=144]",
    "240p": "best[height<=240][ext=mp4]/best[height<=240]",
    "360p": "best[height<=360][ext=mp4]/best[height<=360]",
    "480p": "best[height<=480][ext=mp4]/best[height<=480]",
    "720p": "best[height<=720][ext=mp4]/best[height<=720]",
    "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]",
    "1440p (2K)": "best[height<=1440][ext=mp4]/best[height<=1440]",
    "2160p (4K)": "best[height<=2160][ext=mp4]/best[height<=2160]",
    "Best": "best[ext=mp4]/best",
}

def download_video_or_playlist(url, download_path='downloads', download_type='video', quality='Best', content_type='Video', zip_output=False, zip_filename="videos.zip", progress_hook=None):
    import yt_dlp
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)
    
    ydl_format = VIDEO_OPTIONS.get(quality, "best[ext=mp4]/best")
    is_playlist = (content_type == "Playlist")
    
    # First, extract info to get titles and thumbnails (no download yet)
    info_opts = {
        "quiet": True,
        "extract_flat": False,
        "noplaylist": not is_playlist,
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(info_opts) as ydl_info:
        info = ydl_info.extract_info(url, download=False)
    
    titles = []
    thumbnails = []
    if is_playlist and "entries" in info:
        for entry in info["entries"]:
            if entry:
                titles.append(entry.get("title", "Unknown"))
                thumbnails.append(entry.get("thumbnail", None))
    else:
        titles = [info.get("title", "Unknown")]
        thumbnails = [info.get("thumbnail", None)]
    
    # Now download with progress
    ydl_opts = {
        "format": ydl_format,
        "ignoreerrors": True,
        "quiet": True,
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "noplaylist": not is_playlist,
        "progress_hooks": [progress_hook] if progress_hook else [],
        "no_warnings": True,
        "merge_output_format": None,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error: {e}")
        return None, titles, thumbnails
    
    files = [os.path.join(root, f) for root, _, fs in os.walk(download_path) for f in fs]
    if not files:
        return None, titles, thumbnails
    
    if zip_output and is_playlist and len(files) > 1:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(f, os.path.basename(f))
        buffer.seek(0)
        return buffer.getvalue(), titles, thumbnails
    
    return files[0] if not is_playlist else files, titles, thumbnails
