import os
import io
import zipfile
import shutil

# ------------------------------
# VIDEO QUALITY OPTIONS (PRE-MERGED, NO AUDIO MERGE)
# ------------------------------
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

def download_video_or_playlist(
    url,
    download_path='downloads',
    download_type='video',
    quality='Best',
    content_type='Video',
    zip_output=False,
    zip_filename="downloaded_videos.zip",
    progress_hook=None
):
    import yt_dlp
    # Clean folder
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)
    
    # Format: Always video, pre-merged MP4 (no FFmpeg needed)
    ydl_format = VIDEO_OPTIONS.get(quality, "best[ext=mp4]/best")
    
    is_playlist = (content_type == "Playlist")
    
    # YT-DLP Options: No merging, robust error handling
    ydl_opts = {
        "format": ydl_format,
        "ignoreerrors": True,
        "quiet": True,
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "noplaylist": not is_playlist,
        "extract_flat": False,
        "progress_hooks": [progress_hook] if progress_hook else [],
        "merge_output_format": None,  # Disable merging to avoid FFmpeg
        "no_warnings": True,  # Suppress yt-dlp warnings
    }
    
    # No postprocessors (no audio extraction)
    
    # Download
    playlist_titles = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if is_playlist and "entries" in info:
                playlist_titles = [e.get("title", "Unknown") for e in info["entries"] if e]
            else:
                playlist_titles = [info.get("title", "Unknown")]
    except Exception as e:
        print(f"Download error: {e}")
        return None, []
    
    # Collect files
    downloaded_files = [os.path.join(root, f) for root, _, files in os.walk(download_path) for f in files]
    
    if not downloaded_files:
        return None, playlist_titles
    
    # ZIP if needed
    if zip_output and is_playlist and len(downloaded_files) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for file in downloaded_files:
                z.write(file, os.path.basename(file))
        zip_buffer.seek(0)
        return zip_buffer.getvalue(), playlist_titles
    
    # Single or list
    if not is_playlist:
        return downloaded_files[0], playlist_titles
    return downloaded_files, playlist_titles
