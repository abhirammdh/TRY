# app.py
import streamlit as st
import requests
import os
import io
import zipfile
from datetime import timedelta

# -------------------------
# Page / Theme Setup
# -------------------------
st.set_page_config(page_title="RAVANA · Glass Downloader", layout="wide")

# Custom Glassmorphism styling (dark)
st.markdown("""
<style>
:root {
  --accent: #ff1f52;
  --card-bg: rgba(255,255,255,0.04);
  --muted: #bdbdbd;
}
body {
  background: linear-gradient(180deg,#0b0c0e,#0f1113);
  color: #ffffff;
}
.header {
  text-align:center;
  padding-top:18px;
  padding-bottom:6px;
}
.title {
  font-size:36px;
  font-weight:800;
  color: var(--accent);
  letter-spacing:1px;
  margin-bottom:4px;
}
.subtitle {
  color: var(--muted);
  margin-top:0px;
  margin-bottom:14px;
}
.nav {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius:12px;
  padding:10px;
  margin-bottom:18px;
  border: 1px solid rgba(255,255,255,0.03);
}
.card {
  background: var(--card-bg);
  border-radius:14px;
  padding:18px;
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}
.section-title {
  font-size:18px;
  color:#fff;
  margin-bottom:8px;
  font-weight:700;
}
.small {
  color: var(--muted);
  font-size:13px;
}
.controls .stButton>button {
  background: var(--accent);
  color: white;
  border-radius:10px;
  padding:10px 12px;
  font-weight:700;
}
.controls .stButton>button:hover {
  background: #ff0037;
  transform: translateY(-1px);
}
.input-wide .stTextInput>div>input {
  background: rgba(255,255,255,0.02);
  color: #fff;
}
.selectbox, .radio {
  background: rgba(255,255,255,0.01);
}
.download-list {
  margin-top:8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Sidebar / Navigation
# -------------------------
with st.sidebar:
    st.markdown("<div class='nav'><strong>RAVANA</strong>  ·  VIDEO  ·  AUDIO  ·  PLAYLIST</div>", unsafe_allow_html=True)
    nav = st.radio("Navigate", ["Home", "Downloader", "About"], index=1)
    st.markdown("---")
    st.markdown("Made for quick, reliable downloads — glass theme.")
    st.markdown("")

# -------------------------
# Header
# -------------------------
st.markdown("<div class='header'><div class='title'>RAVANA YT DOWNLOADER</div><div class='subtitle'>Dark glass • two-column pro layout • simple controls</div></div>", unsafe_allow_html=True)

# -------------------------
# Helper functions (import yt_dlp inside to avoid import-time errors)
# -------------------------
def fetch_info(url):
    """
    Fetch metadata via yt-dlp (imported inside).
    Returns dict with title, thumbnail, uploader, duration (seconds), formats.
    Raises Exception if yt-dlp not available.
    """
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp is not installed on the server. Add 'yt-dlp' to requirements.txt and redeploy.")

    opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        data = ydl.extract_info(url, download=False)
    # normalize
    info = {
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "uploader": data.get("uploader"),
        "duration": data.get("duration"),
        "formats": data.get("formats", []),
        "is_playlist": data.get("_type") == "playlist"
    }
    return info

def choose_format_id(formats, want_video, quality_label):
    """
    Find a format id that best matches the requested quality_label.
    quality_label examples:
      video: '240p','360p','480p','720p','1080p','1440p','2160p'
      audio: '64kbps','128kbps','192kbps','320kbps'
    """
    # prefer progressive (video+audio) or combine video+audio if necessary
    if want_video:
        # prefer the bestvideo with height <= requested height plus bestaudio fallback
        try:
            target = int(quality_label.replace("p",""))
        except:
            target = None

        # Try to find progressive format with exact height
        candidates = []
        for f in formats:
            # some formats include "height"
            h = f.get("height")
            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            if vcodec != "none":
                # score: how close to target (prefer <= target)
                if target and h:
                    if h == target:
                        return f.get("format_id")
                    candidates.append((abs((h or 0)-target), f.get("format_id"), h))
        # fallback: choose nearest height
        if candidates:
            candidates.sort(key=lambda x: (x[0], - (x[2] or 0)))
            return candidates[0][1]
        # final fallback: return 'bestvideo+bestaudio/best'
        return "bestvideo+bestaudio/best"

    else:
        # audio selection based on abr
        try:
            target_k = int(quality_label.replace("kbps",""))
        except:
            target_k = None

        audio_cands = []
        for f in formats:
            if f.get("acodec") != "none" and f.get("vcodec") == "none":
                abr = f.get("abr")  # may be float
                if abr:
                    audio_cands.append((abs((abr or 0) - (target_k or 0)), f.get("format_id"), abr))
        if audio_cands:
            audio_cands.sort(key=lambda x: (x[0], - (x[2] or 0)))
            return audio_cands[0][1]
        return "bestaudio/best"

def download_and_package(url, format_id, download_type, is_playlist, zip_output, zip_name):
    """
    Downloads using yt-dlp (imports inside).
    Returns: if zip_output -> bytes buffer (io.BytesIO), else list of file paths downloaded.
    """
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp is not installed on the server. Add 'yt-dlp' to requirements.txt and redeploy.")

    out_folder = "downloads"
    # clean out folder for each run
    if os.path.exists(out_folder):
        # remove previous files safely
        for fn in os.listdir(out_folder):
            try:
                os.remove(os.path.join(out_folder, fn))
            except:
                pass
    else:
        os.makedirs(out_folder, exist_ok=True)

    # Create ydl options
    ydl_opts = {
        "format": format_id,
        "outtmpl": os.path.join(out_folder, "%(title)s.%(ext)s"),
        "noplaylist": not is_playlist,
        "quiet": True,
        "ignoreerrors": True
    }

    if download_type == "audio":
        # convert to mp3 using ffmpeg (if available in environment)
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",  # yt-dlp uses 0-320; we use a safe default; actual kbps mapping handled by format selection
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")

    # collect files
    downloaded = []
    for root, _, files in os.walk(out_folder):
        for f in files:
            downloaded.append(os.path.join(root, f))

    if zip_output:
        # build zip in-memory
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in downloaded:
                zf.write(fp, arcname=os.path.basename(fp))
        zip_buf.seek(0)
        return zip_buf, downloaded
    else:
        return None, downloaded

# -------------------------
# Home / About
# -------------------------
if nav == "Home":
    st.markdown("<div class='card'><div class='section-title'>Welcome</div><div class='small'>Use the Downloader page to fetch a YouTube URL, preview its thumbnail and metadata, then choose Video or Audio quality and download. The UI uses glass-style cards with a two-column layout.</div></div>", unsafe_allow_html=True)
    st.stop()

if nav == "About":
    st.markdown("<div class='card'><div class='section-title'>About</div><div class='small'>Ravana Downloader — built to be clean and straightforward. Add 'yt-dlp' to requirements.txt for the downloader to function in hosted environments. This UI provides a left preview column and right controls column for a pro workflow.</div></div>", unsafe_allow_html=True)
    st.stop()

# -------------------------
# Downloader Page (main)
# -------------------------
# Layout: left column (preview), right column (controls)
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Preview</div>", unsafe_allow_html=True)

    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

    metadata = None
    fetched = False

    if url and url.strip():
        try:
            metadata = fetch_info(url)
            fetched = True
        except ModuleNotFoundError as me:
            st.error(str(me))
        except Exception as e:
            st.error(f"Could not fetch info: {e}")

    if fetched and metadata:
        # show thumbnail, title, uploader, duration
        thumb = metadata.get("thumbnail")
        title = metadata.get("title") or "Unknown title"
        uploader = metadata.get("uploader") or ""
        duration = metadata.get("duration")
        is_playlist = metadata.get("is_playlist", False)

        if thumb:
            st.image(thumb, width=420)

        st.markdown(f"**{title}**")
        st.markdown(f"<div class='small'>Channel: {uploader}</div>", unsafe_allow_html=True)
        if duration:
            td = str(timedelta(seconds=int(duration)))
            st.markdown(f"<div class='small'>Duration: {td}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>")

        # quick summary of video vs playlist
        st.markdown(f"<div class='small'>Detected type: {'Playlist' if is_playlist else 'Single video'}</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='small'>Enter a YouTube URL to preview title, thumbnail and meta information.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Download Options</div>", unsafe_allow_html=True)

    # Controls only available after successful fetch
    if not (fetched and metadata):
        st.markdown("<div class='small'>Preview a URL first, then choose options on the right and click Download.</div>", unsafe_allow_html=True)
    else:
        # Download type
        dl_type = st.radio("Type", ["Video", "Audio"], horizontal=True)
        is_audio = dl_type == "Audio"

        # Content: let user override playlist detection
        content_type = st.radio("Content", ["Single", "Playlist"], index=0 if not metadata.get("is_playlist") else 1, horizontal=True)
        is_playlist = content_type == "Playlist"

        # Quality options (simple list — no confusion)
        if is_audio:
            audio_choices = ["64kbps", "128kbps", "192kbps", "320kbps"]
            sel_audio = st.selectbox("Audio bitrate", audio_choices, index=1)
            quality_label = sel_audio
        else:
            video_choices = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p (4K)"]
            sel_video = st.selectbox("Resolution", video_choices, index=5)
            # normalize 2160p label
            quality_label = sel_video.replace(" (4K)", "")

        zip_output = False
        if is_playlist:
            zip_output = st.checkbox("Produce ZIP of all files", value=True)
            if zip_output:
                zip_name = st.text_input("ZIP filename (without .zip)", value=(metadata.get("title") or "playlist").replace(" ", "_"))
                if not zip_name:
                    zip_name = (metadata.get("title") or "playlist").replace(" ", "_")
        else:
            zip_name = (metadata.get("title") or "download").replace(" ", "_")

        # Fetch best matching format id (uses formats from metadata)
        # Guard if formats empty
        format_id = None
        if metadata.get("formats"):
            try:
                format_id = choose_format_id(metadata["formats"], not is_audio, quality_label)
            except Exception:
                format_id = None

        # Download button
        if st.button("Download"):
            if format_id is None:
                st.error("No matching format was found for this request.")
            else:
                # perform download
                with st.spinner("Downloading — this may take a while depending on quality and file size..."):
                    try:
                        zip_buf, downloaded_files = download_and_package(
                            url=url,
                            format_id=format_id,
                            download_type=("audio" if is_audio else "video"),
                            is_playlist=is_playlist,
                            zip_output=zip_output,
                            zip_name=zip_name
                        )
                    except ModuleNotFoundError as me:
                        st.error(str(me))
                        st.stop()
                    except Exception as e:
                        st.error(f"Download failed: {e}")
                        st.stop()

                # Provide outputs
                if zip_output:
                    # zip_buf contains the in-memory zip
                    filename = f"{zip_name}.zip"
                    st.success("Download ready")
                    st.download_button("Download ZIP", data=zip_buf.getvalue(), file_name=filename)
                else:
                    st.success("Files ready")
                    st.markdown("<div class='download-list'>", unsafe_allow_html=True)
                    for fp in downloaded_files:
                        base = os.path.basename(fp)
                        with open(fp, "rb") as fh:
                            st.download_button(f"Save: {base}", data=fh.read(), file_name=base)
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# End
# -------------------------
st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

