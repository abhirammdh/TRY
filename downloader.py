import os
import io
import zipfile
import shutil

# ------------------------------
# AUDIO + VIDEO QUALITY OPTIONS
# ------------------------------
AUDIO_OPTIONS = {
    "64": "bestaudio[abr<=64]/bestaudio",
    "128": "bestaudio[abr<=128]/bestaudio",
    "192": "bestaudio[abr<=192]/bestaudio",
    "256": "bestaudio[abr<=256]/bestaudio",
    "320": "bestaudio[abr<=320]/bestaudio",
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
    zip_filename="downloaded_videos.zip",
    progress_hook=None  # Ensure this param is here
):
    """
    Download a single video/audio or playlist from YouTube with progress hook.
    
    Args:
        ... (existing)
        progress_hook: Function to call on progress updates (yt-dlp hook).
    
    Returns:
        Tuple: (data_or_files, titles)
    """
    import yt_dlp  # Safe import inside function
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
        "extract_flat": False,  # Download full info
        "progress_hooks": [progress_hook] if progress_hook else [],  # Add hook
    }
    
    # Suppress FFmpeg warnings minimally
    ydl_opts["no_warnings"] = False
    
    # ------------------------------
    # APPLY MP3 POSTPROCESSOR (DYNAMIC QUALITY)
    # ------------------------------
    if download_type == "audio":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": quality,  # Use selected quality (e.g., "128")
        }]
    
    # ------------------------------
    # DOWNLOAD
    # ------------------------------
    playlist_titles = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Collect titles (for single or playlist)
            if is_playlist and "entries" in info:
                playlist_titles = [e.get("title", "Unknown") for e in info["entries"] if e]
            else:
                playlist_titles = [info.get("title", "Unknown")]
    except Exception as e:
        print(f"Download error: {e}")  # Log for debugging
        return None, []
    
    # ------------------------------
    # COLLECT DOWNLOADED FILES
    # ------------------------------
    downloaded_files = []
    for root, _, files in os.walk(download_path):
        for f in files:
            downloaded_files.append(os.path.join(root, f))
    
    if not downloaded_files:
        return None, playlist_titles
    
    # ------------------------------
    # ZIP OUTPUT (USE PROVIDED FILENAME)
    # ------------------------------
    if zip_output and is_playlist and len(downloaded_files) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for file in downloaded_files:
                z.write(file, os.path.basename(file))
        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()  # Return bytes for easy use in Streamlit
        return zip_data, playlist_titles
    
    # For single or non-zip playlist: return first file if single, else list
    if not is_playlist:
        return downloaded_files[0], playlist_titles
    return downloaded_files, playlist_titles
