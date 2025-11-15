import os
import yt_dlp


# ---------------------------------------------------------
#  Create folder safely
# ---------------------------------------------------------
def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


# ---------------------------------------------------------
#  DOWNLOAD VIDEO (MP4)
# ---------------------------------------------------------
def download_video(url, quality="720p"):
    folder = make_folder("downloads/videos")

    height = quality.replace("p", "")

    ydl_opts = {
        "format": f"bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/mp4",
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename


# ---------------------------------------------------------
#  DOWNLOAD AUDIO (M4A)
# ---------------------------------------------------------
def download_audio(url):
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
#  DOWNLOAD PLAYLIST (VIDEO)
# ---------------------------------------------------------
def download_playlist_video(url, quality="720p"):
    folder = make_folder("downloads/playlist_videos")
    height = quality.replace("p", "")

    ydl_opts = {
        "format": f"bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/mp4",
        "outtmpl": f"{folder}/%(playlist_index)s - %(title)s.%(ext)s",
        "quiet": True
    }

    downloaded_files = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(url, download=True)

        if "entries" in playlist:
            for entry in playlist["entries"]:
                if entry:
                    downloaded_files.append(ydl.prepare_filename(entry))

    return downloaded_files


# ---------------------------------------------------------
#  DOWNLOAD PLAYLIST (AUDIO)
# ---------------------------------------------------------
def download_playlist_audio(url):
    folder = make_folder("downloads/playlist_audios")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/m4a",
        "outtmpl": f"{folder}/%(playlist_index)s - %(title)s.m4a",
        "quiet": True
    }

    downloaded_files = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(url, download=True)

        if "entries" in playlist:
            for entry in playlist["entries"]:
                if entry:
                    downloaded_files.append(ydl.prepare_filename(entry))

    return downloaded_files


# ---------------------------------------------------------
#  UNIVERSAL HANDLER
# ---------------------------------------------------------
def download_video_or_playlist(url, quality="720p", mode="video"):
    is_playlist = ("playlist" in url) or ("list=" in url)

    if is_playlist:
        if mode == "video":
            return download_playlist_video(url, quality)
        else:
            return download_playlist_audio(url)
    else:
        if mode == "video":
            return [download_video(url, quality)]
        else:
            return [download_audio(url)]


