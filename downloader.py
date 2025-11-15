import os
import yt_dlp


# Create folder
def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


# ---------------------------------------------------------
#  EXTRACT VIDEO DETAILS (title, thumbnail, views, etc.)
# ---------------------------------------------------------
def get_video_info(url):
    ydl_opts = {"quiet": True, "skip_download": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "views": info.get("view_count"),
        "channel": info.get("channel"),
        "upload_date": info.get("upload_date"),
    }


# ---------------------------------------------------------
#  DOWNLOAD BEST VIDEO (MP4)
# ---------------------------------------------------------
def download_best_video(url):
    folder = make_folder("downloads/videos")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "quiet": True,
        "merge_output_format": "mp4"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename


# ---------------------------------------------------------
#  DOWNLOAD BEST AUDIO (M4A)
# ---------------------------------------------------------
def download_best_audio(url):
    folder = make_folder("downloads/audios")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/m4a",
        "outtmpl": f"{folder}/%(title)s.m4a",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename


# ---------------------------------------------------------
#  UNIVERSAL ENTRY (video / audio)
# ---------------------------------------------------------
def download_video_or_playlist(url, mode="video"):
    is_playlist = ("list=" in url or "playlist" in url)

    # ------------ Playlist ------------
    if is_playlist:
        folder = make_folder(f"downloads/playlist_{mode}s")

        if mode == "video":
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
        else:
            fmt = "bestaudio[ext=m4a]/m4a"

        ydl_opts = {
            "format": fmt,
            "outtmpl": f"{folder}/%(playlist_index)s - %(title)s.%(ext)s",
            "quiet": True,
            "merge_output_format": "mp4",
        }

        out_files = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist = ydl.extract_info(url, download=True)
            for entry in playlist["entries"]:
                if entry:
                    out_files.append(ydl.prepare_filename(entry))

        return out_files

    # ------------ Single Video ------------
    if mode == "video":
        return [download_best_video(url)]
    else:
        return [download_best_audio(url)]
