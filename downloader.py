
import os
import io
import zipfile
import shutil

QUALITY_OPTIONS = {
    'Best': 'best',
    'Worst': 'worst',
    '480p': 'bestvideo[height<=480]+bestaudio/best',
    '720p': 'bestvideo[height<=720]+bestaudio/best',
    '1080p': 'bestvideo[height<=1080]+bestaudio/best'
}

def download_video_or_playlist(
    url,
    download_path='downloads',
    download_type='video',
    quality='Best',
    content_type='Playlist',
    zip_output=False
):
    # FIX → import yt_dlp inside function
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise Exception("yt-dlp is not installed. Add `yt-dlp` to requirements.txt")

    # Clean folder
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)

    is_playlist = (content_type == 'Playlist')
    ydl_format = 'bestaudio/best' if download_type == 'audio' else QUALITY_OPTIONS.get(quality, 'best')

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': not is_playlist,
        'quiet': True,
        'ignoreerrors': True,
    }

    if download_type == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")

    # Collect downloaded files
    downloaded_filepaths = []
    for root, _, files in os.walk(download_path):
        for file in files:
            downloaded_filepaths.append(os.path.join(root, file))

    # Zip option
    if zip_output and downloaded_filepaths:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in downloaded_filepaths:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)
        zip_buffer.seek(0)
        return zip_buffer

    return downloaded_filepaths
