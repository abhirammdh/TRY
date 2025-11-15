import yt_dlp
import os

def download_youtube(url, folder, progress_hook=None):
    if not os.path.exists(folder):
        os.makedirs(folder)

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
    }

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, "Download completed successfully."
    except Exception as e:
        return False, "Error: " + str(e)
