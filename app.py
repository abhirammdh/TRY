# app.py
import streamlit as st
import os
import io
import zipfile
from datetime import timedelta

st.set_page_config(page_title="RAVANA YT DOWNLOADER", layout="wide")

# ---------------------------
# Session / Theme
# ---------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

def set_theme(mode):
    st.session_state.theme_mode = mode

# Sidebar controls
with st.sidebar:
    st.markdown("## Ravana Settings")
    mode = st.selectbox("Theme", ["dark (black+green)", "light (white+violet)"],
                        index=0 if st.session_state.theme_mode=="dark" else 1)
    set_theme("dark" if mode.startswith("dark") else "light")
    st.markdown("---")
    page = st.radio("Navigate", ["Home", "Video", "Audio", "Playlist", "About"], index=1)

# ---------------------------
# CSS (glass + subtle animation on main button)
# ---------------------------
if st.session_state.theme_mode == "dark":
    accent = "#00ff66"
    bg1 = "#050606"
    bg2 = "#0b0d0f"
    muted = "#9aa6a0"
    btn_text = "#000000"
else:
    accent = "#7a44ff"
    bg1 = "#ffffff"
    bg2 = "#f4f2fb"
    muted = "#666080"
    btn_text = "#ffffff"

st.markdown(f"""
<style>
:root {{
  --accent: {accent};
  --bg1: {bg1};
  --bg2: {bg2};
  --muted: {muted};
  --btn-text: {btn_text};
}}
html, body, .reportview-container, .main {{
  background: linear-gradient(180deg, var(--bg1), var(--bg2)) !important;
}}
.card {{
  background: rgba(255,255,255,0.02);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255,255,255,0.03);
  box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}}
.header-title {{
  font-size:28px;
  font-weight:800;
  color: var(--accent);
  margin-bottom:6px;
}}
.subtitle {{ color: var(--muted); margin-bottom:12px; }}
.main-btn > button{{
  background: var(--accent) !important;
  color: var(--btn-text) !important;
  border-radius:10px;
  padding:10px 18px;
  font-weight:700;
  transition: transform 0.15s ease-in-out;
}}
/* subtle scale animation (no glow) */
.main-btn > button:active {{
  transform: scale(0.98);
}}
.thumb-img {{ border-radius:8px; }}
.small-muted {{ color: var(--muted); font-size:13px; }}
.progress-label {{ color: var(--muted); font-size:13px; }}
.table-header {{ font-weight:700; color:var(--muted); padding:8px 0; display:flex; }}
.table-row {{ display:flex; align-items:center; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.03); }}
.col-thumb {{ width:120px; }}
.col-title {{ flex:1; padding-left:12px; }}
.col-duration {{ width:90px; text-align:left; }}
.col-action {{ width:160px; text-align:left; }}
@media (max-width:900px) {{
  .col-thumb {{ width:80px; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Helper utilities
# ---------------------------
def sec_to_hms(sec):
    if not sec:
        return ""
    return str(timedelta(seconds=int(sec)))

def fetch_info(url):
    """Return yt-dlp metadata dict. Imports yt_dlp inside."""
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp not installed. Add 'yt-dlp' to requirements.txt")
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

def download_single_with_progress(url, format_selector, out_folder, filename_prefix, download_type, progress_callback):
    """
    Downloads a single item via yt-dlp without merging (uses single-format selectors like best[height<=720] or bestaudio[abr<=128]).
    progress_callback receives percentages rounded to 10 (10,20,...100).
    """
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp not installed. Add 'yt-dlp' to requirements.txt")

    os.makedirs(out_folder, exist_ok=True)
    outtmpl = os.path.join(out_folder, f"{filename_prefix}.%(ext)s")

    ydl_opts = {
        "format": format_selector,
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "ignoreerrors": False
    }

    if download_type == "audio":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    # progress hook
    def _hook(d):
        if d.get("status") == "downloading":
            dl = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            try:
                pct = int(dl / total * 100)
                pct_10 = min(100, max(0, ((pct + 9) // 10) * 10))
                progress_callback(pct_10)
            except Exception:
                progress_callback(0)
        elif d.get("status") == "finished":
            progress_callback(100)

    ydl_opts["progress_hooks"] = [_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # find downloaded file
    downloaded_file = None
    for fname in os.listdir(out_folder):
        if fname.startswith(filename_prefix):
            downloaded_file = os.path.join(out_folder, fname)
            break
    return downloaded_file

# ---------------------------
# UI: Home
# ---------------------------
if page == "Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>RAVANA YT DOWNLOADER</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Fast • Clear • No-merge downloads (Video and Audio are separate)</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>This tool shows separate pages for Video, Audio and Playlist downloads. Video downloads use single-format selections (no `bestvideo+bestaudio` merging). Playlist page lists all videos in a compact table — download any item individually or download the entire playlist as a ZIP. Progress updates in 10% increments.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------
# UI: Video Page
# ---------------------------
if page == "Video":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>Video Downloader</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Pick resolution — downloads do NOT merge audio automatically (no bestvideo+bestaudio). If a high-res progressive stream isn't available, the file may be video-only.</div>", unsafe_allow_html=True)

    url = st.text_input("YouTube video URL", key="video_url")
    if url:
        try:
            info = fetch_info(url)
        except Exception as e:
            st.error(f"Could not fetch info: {e}")
            info = None

        if info:
            if info.get("thumbnail"):
                st.image(info.get("thumbnail"), width=420)
            st.markdown(f"**{info.get('title','')}**")
            st.markdown(f"<div class='small-muted'>Channel: {info.get('uploader','')}</div>", unsafe_allow_html=True)
            if info.get("duration"):
                st.markdown(f"<div class='small-muted'>Duration: {sec_to_hms(info.get('duration'))}</div>", unsafe_allow_html=True)

            # Quality choices (single-format selectors: best[height<=...])
            resolution = st.selectbox("Resolution", ["144p","240p","360p","480p","720p","1080p","1440p (2K)","2160p (4K)"], index=5)
            # map to selector
            res_map = {
                "144p": "best[height<=144]",
                "240p": "best[height<=240]",
                "360p": "best[height<=360]",
                "480p": "best[height<=480]",
                "720p": "best[height<=720]",
                "1080p": "best[height<=1080]",
                "1440p (2K)": "best[height<=1440]",
                "2160p (4K)": "best[height<=2160]"
            }
            format_selector = res_map[resolution]
            out_folder = "downloads_video"

            if st.button("Download Video", key="video_dl", help="Single Download — no merge"):
                progress_bar = st.progress(0)
                status = st.empty()
                def report(p):
                    progress_bar.progress(p)
                    status.markdown(f"<div class='progress-label'>{p}%</div>", unsafe_allow_html=True)
                try:
                    title_prefix = (info.get("title") or "video").replace(" ", "_")[:120]
                    downloaded_file = download_single_with_progress(url, format_selector, out_folder, title_prefix, "video", report)
                    if downloaded_file and os.path.exists(downloaded_file):
                        status.markdown("<div class='small-muted'>Download ready</div>", unsafe_allow_html=True)
                        with open(downloaded_file, "rb") as fh:
                            st.download_button("Save video", data=fh.read(), file_name=os.path.basename(downloaded_file), mime="video/mp4")
                    else:
                        st.error("Download failed or no file found.")
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# UI: Audio Page
# ---------------------------
if page == "Audio":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>Audio Downloader</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Download audio-only tracks at various kbps. No video/audio merging here.</div>", unsafe_allow_html=True)

    a_url = st.text_input("YouTube URL (audio)", key="audio_url")
    if a_url:
        try:
            info = fetch_info(a_url)
        except Exception as e:
            st.error(f"Could not fetch info: {e}")
            info = None

        if info:
            if info.get("thumbnail"):
                st.image(info.get("thumbnail"), width=320)
            st.markdown(f"**{info.get('title','')}**")
            bitrate = st.selectbox("Choose bitrate (kbps)", ["64","128","192","256","320","360"], index=1)
            format_selector = f"bestaudio[abr<={bitrate}]"
            out_folder = "downloads_audio"
            if st.button("Download Audio", key="audio_dl"):
                pbar = st.progress(0)
                status = st.empty()
                def report(p):
                    pbar.progress(p)
                    status.markdown(f"<div class='progress-label'>{p}%</div>", unsafe_allow_html=True)
                try:
                    title_prefix = (info.get("title") or "audio").replace(" ", "_")[:120]
                    downloaded_file = download_single_with_progress(a_url, format_selector, out_folder, title_prefix, "audio", report)
                    if downloaded_file and os.path.exists(downloaded_file):
                        status.markdown("<div class='small-muted'>Download ready</div>", unsafe_allow_html=True)
                        with open(downloaded_file, "rb") as fh:
                            st.download_button("Save audio", data=fh.read(), file_name=os.path.basename(downloaded_file), mime="audio/mpeg")
                    else:
                        st.error("Download failed or no file found.")
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# UI: Playlist Page
# ---------------------------
if page == "Playlist":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>Playlist Downloader</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Playlist is listed in a compact table. You can download individual items (file per item) or download the entire playlist as a ZIP (uses downloader.py).</div>", unsafe_allow_html=True)

    pl_url = st.text_input("Playlist URL", key="playlist_url")
    if pl_url:
        try:
            info = fetch_info(pl_url)
        except Exception as e:
            st.error(f"Could not fetch playlist: {e}")
            info = None

        entries = []
        if info and info.get("_type") == "playlist" and info.get("entries"):
            for e in info.get("entries"):
                if not e:
                    continue
                entries.append({
                    "title": e.get("title") or "Untitled",
                    "url": e.get("webpage_url") or e.get("url") or "",
                    "thumbnail": e.get("thumbnail"),
                    "duration": e.get("duration")
                })

        if entries:
            # Table header
            st.markdown("<div class='table-header'><div class='col-thumb'>Thumbnail</div><div class='col-title'>Title</div><div class='col-duration'>Duration</div><div class='col-action'>Download</div></div>", unsafe_allow_html=True)
            for idx, it in enumerate(entries):
                cols = st.columns([0.9, 3.2, 0.8, 1.6])
                with cols[0]:
                    if it.get("thumbnail"):
                        st.image(it["thumbnail"], width=100)
                with cols[1]:
                    st.markdown(f"<div style='font-weight:700'>{it.get('title')}</div>", unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"<div class='small-muted'>{sec_to_hms(it.get('duration'))}</div>", unsafe_allow_html=True)
                with cols[3]:
                    # Per-item controls
                    dl_type = st.selectbox("Type", ["Video","Audio"], key=f"pl_type_{idx}")
                    if dl_type == "Video":
                        res = st.selectbox("Res", ["360p","480p","720p","1080p","1440p","2160p (4K)"], key=f"pl_res_{idx}", index=2)
                        res_map = {
                            "360p":"best[height<=360]",
                            "480p":"best[height<=480]",
                            "720p":"best[height<=720]",
                            "1080p":"best[height<=1080]",
                            "1440p":"best[height<=1440]",
                            "2160p (4K)":"best[height<=2160]"
                        }
                        fmt = res_map[res]
                    else:
                        abr = st.selectbox("Kbps", ["64","128","192","256","320"], key=f"pl_ab_{idx}", index=1)
                        fmt = f"bestaudio[abr<={abr}]"

                    pbar = st.empty()
                    status_lbl = st.empty()
                    if st.button("Download item", key=f"pl_dl_{idx}"):
                        item_url = it.get("url")
                        if not item_url:
                            st.error("URL not available for this item.")
                        else:
                            out_folder = "downloads_playlist"
                            prefix = (it.get("title") or f"item_{idx}").replace(" ", "_")[:120]
                            def report(p):
                                pbar.progress(p)
                                status_lbl.markdown(f"<div class='progress-label'>{p}%</div>", unsafe_allow_html=True)
                            try:
                                path = download_single_with_progress(item_url, fmt, out_folder, prefix, "audio" if dl_type=="Audio" else "video", report)
                                if path and os.path.exists(path):
                                    st.success("Downloaded: " + os.path.basename(path))
                                    with open(path, "rb") as fh:
                                        st.download_button("Save file", data=fh.read(), file_name=os.path.basename(path))
                                else:
                                    st.error("Download failed or file missing.")
                            except Exception as e:
                                st.error(f"Download failed: {e}")
        else:
            st.markdown("<div class='small-muted'>Enter a playlist URL to list items.</div>", unsafe_allow_html=True)

        st.markdown("<hr>")
        st.markdown("### Full playlist ZIP")
        zip_opt = st.checkbox("Download full playlist as ZIP (server-side)")
        zip_name = st.text_input("ZIP name (no .zip)", value="playlist_download")
        if zip_opt and st.button("Create playlist ZIP"):
            # call downloader.py's function (assumes downloader.py exists and uses zip_output=True)
            try:
                from downloader import download_video_or_playlist
            except ModuleNotFoundError:
                st.error("downloader.py missing or yt-dlp not installed there. Ensure downloader.py exists & yt-dlp in requirements.")
                st.stop()
            try:
                st.info("Downloading playlist (server) and packaging ZIP — may take time.")
                # Call with parameters that the downloader expects. We choose 'Best' quality key mapping to its internal options
                res = download_video_or_playlist(
                    url=pl_url,
                    download_path="downloads_playlist_full",
                    download_type="video",
                    quality="Best",
                    content_type="Playlist",
                    zip_output=True,
                    zip_filename=f"{zip_name}.zip" if "zip_filename" in (download_video_or_playlist.__code__.co_varnames) else None
                )
                # downloader.py may return BytesIO or list; handle both
                if isinstance(res, tuple) and isinstance(res[0], io.BytesIO):
                    buf = res[0]
                    st.download_button("Download ZIP", data=buf.getvalue(), file_name=f"{zip_name}.zip")
                elif isinstance(res, io.BytesIO):
                    st.download_button("Download ZIP", data=res.getvalue(), file_name=f"{zip_name}.zip")
                elif isinstance(res, list):
                    # create zip from list
                    mem = io.BytesIO()
                    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
                        for p in res:
                            if os.path.exists(p):
                                zf.write(p, arcname=os.path.basename(p))
                    mem.seek(0)
                    st.download_button("Download ZIP", data=mem.getvalue(), file_name=f"{zip_name}.zip")
                else:
                    st.error("Downloader returned unexpected result.")
            except Exception as e:
                st.error(f"Playlist ZIP failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# About (footer)
# ---------------------------
if page == "About":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>About</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Created by D. Abhiram<br>Studying B.Sc. Computer Science, Sri Sathya Sai Institute of Higher Learning (SSSIHL), Nandigiri Campus.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

