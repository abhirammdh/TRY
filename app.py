# app.py
"""
RAVANA YT DOWNLOADER - Full featured Streamlit app (single file).
Features:
- Dark (black+green) and Light (white+violet) themes
- Glassmorphism cards + subtle animated background
- Thumbnail + metadata preview
- Video (144p -> 4K) and Audio (64kbps -> 360kbps) quality selection
- Individual item downloads for playlists (table style) with per-item progress (10% increments)
- Full-playlist download as ZIP using downloader.download_video_or_playlist (keeps compatibility)
- Rename ZIP name
- Home and About pages (About contains your author text)
- Imports yt_dlp inside functions to avoid import-time crashes on Streamlit Cloud
NOTE: Keep your downloader.py (as provided earlier) in same folder.
Also include a requirements.txt with: streamlit, yt-dlp
"""

import streamlit as st
import requests
import os
import io
import zipfile
from datetime import timedelta

st.set_page_config(page_title="RAVANA · Downloader", layout="wide", initial_sidebar_state="expanded")

# ---------------------------
# Session state defaults
# ---------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# ---------------------------
# Sidebar (navigation + theme)
# ---------------------------
with st.sidebar:
    st.markdown("## Ravana — Settings")
    theme_choice = st.selectbox("Theme", ["dark (black/green)", "light (white/violet)"],
                                index=0 if st.session_state.theme_mode == "dark" else 1)
    st.session_state.theme_mode = "dark" if theme_choice.startswith("dark") else "light"
    st.markdown("---")
    nav = st.radio("Navigate", ["Home", "Downloader", "About"], index=1)
    st.markdown("---")
    st.markdown("Made with care — D. Abhiram")

# ---------------------------
# Theme variables and CSS (glass + animation)
# ---------------------------
if st.session_state.theme_mode == "dark":
    accent = "#00ff66"  # neon green
    bg_top = "#050606"
    bg_bottom = "#0b0f10"
    text_muted = "#9aa6a0"
    btn_text = "#000000"
else:
    accent = "#7a44ff"  # violet
    bg_top = "#ffffff"
    bg_bottom = "#f4f2fb"
    text_muted = "#6a5a80"
    btn_text = "#ffffff"

st.markdown(f"""
<style>
:root {{
  --accent: {accent};
  --bg-top: {bg_top};
  --bg-bottom: {bg_bottom};
  --muted: {text_muted};
  --btn-text: {btn_text};
}}

/* Animated gradient background */
.main > div {{
  background: linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
}}
/* subtle moving gradient layer */
.bg-anim {{
  position: fixed;
  inset: 0;
  z-index: -1;
  background: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.02), transparent 5%),
              radial-gradient(circle at 90% 80%, rgba(255,255,255,0.02), transparent 6%);
  animation: float 18s ease-in-out infinite;
  pointer-events: none;
  opacity: 0.9;
}}
@keyframes float {{
  0% {{ transform: translateY(-10px) translateX(0px); }}
  50% {{ transform: translateY(10px) translateX(8px); }}
  100% {{ transform: translateY(-10px) translateX(0px); }}
}}

/* Cards / glass */
.card {{
  background: rgba(255,255,255,0.02);
  border-radius: 14px;
  padding: 18px;
  border: 1px solid rgba(255,255,255,0.03);
  box-shadow: 0 12px 30px rgba(0,0,0,0.6);
}}
.header-title {{
  font-size: 28px;
  font-weight: 800;
  color: var(--accent);
  margin-bottom: 6px;
}}
.subtitle {{ color: var(--muted); margin-bottom: 12px; }}
.small-muted {{ color: var(--muted); font-size:13px; }}

/* Buttons */
.controls .stButton>button {{
  background: var(--accent) !important;
  color: var(--btn-text) !important;
  border-radius: 10px;
  font-weight:700;
}}
.controls .stButton>button:hover {{
  transform: translateY(-2px);
}}
.download-btn-small .stButton>button {{
  padding:6px 10px;
  font-size:13px;
}}

/* Table like rows */
.playlist-row {{
  padding:10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  display:flex;
  align-items:center;
}}
.thumb-img {{
  border-radius:6px;
}}
.progress-label {{ color: var(--muted); font-size:13px; }}

/* responsive */
@media (max-width: 900px) {{
  .thumb-img {{ width: 80px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# animated background div
st.markdown("<div class='bg-anim'></div>", unsafe_allow_html=True)


# ---------------------------
# Helper functions (yt-dlp inside functions)
# ---------------------------
def fetch_metadata(url):
    """Return metadata dict from yt-dlp (title, thumbnail, uploader, duration, formats, entries if playlist)"""
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp is not installed. Add 'yt-dlp' to requirements.txt and redeploy.")

    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


def sec_to_hms(sec):
    if not sec:
        return ""
    return str(timedelta(seconds=int(sec)))


def choose_format_id(formats, want_video, quality_label):
    """
    Choose a format_id matching the requested quality.
    If video: prefer progressive (video+audio), else choose bestvideo+bestaudio fallback.
    If audio: choose format with abr closest to target.
    """
    if not formats:
        return None

    if want_video:
        # parse target height (e.g., '720' from '720p')
        try:
            target = int(quality_label.replace("p", ""))
        except:
            target = None
        progressive = []
        video_only = []
        for f in formats:
            h = f.get("height")
            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            fmt_id = f.get("format_id")
            # progressive: has both video & audio
            if vcodec != "none" and acodec != "none":
                progressive.append((h or 0, fmt_id))
            elif vcodec != "none":
                video_only.append((h or 0, fmt_id))
        # look for exact or nearest progressive
        candidates = progressive or video_only
        if candidates and target:
            candidates.sort(key=lambda x: (abs((x[0] or 0) - target), - (x[0] or 0)))
            return candidates[0][1]
        elif candidates:
            # return highest available progressive
            candidates.sort(key=lambda x: (- (x[0] or 0)))
            return candidates[0][1]
        return "bestvideo+bestaudio/best"
    else:
        # audio selection by abr
        try:
            target_k = int(quality_label.replace("kbps", ""))
        except:
            target_k = None
        audio_cands = []
        for f in formats:
            if f.get("acodec") != "none" and f.get("vcodec") == "none":
                abr = f.get("abr")
                if abr:
                    audio_cands.append((abs((abr or 0) - (target_k or 0)), f.get("format_id"), abr))
        if audio_cands:
            audio_cands.sort(key=lambda x: (x[0], - (x[2] or 0)))
            return audio_cands[0][1]
        return "bestaudio/best"


def download_with_progress(target_url, format_id, out_folder, filename_prefix, download_type, progress_callback):
    """
    Download a single URL with yt-dlp and call progress_callback(percent_rounded_to_10).
    Returns downloaded file path.
    """
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("yt-dlp is not installed. Add 'yt-dlp' to requirements.txt and redeploy.")

    os.makedirs(out_folder, exist_ok=True)
    outtmpl = os.path.join(out_folder, f"{filename_prefix}.%(ext)s")
    ydl_opts = {
        "format": format_id,
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
        ydl.download([target_url])

    # find downloaded file
    downloaded_file = None
    for fname in os.listdir(out_folder):
        if fname.startswith(filename_prefix):
            downloaded_file = os.path.join(out_folder, fname)
            break
    return downloaded_file


# ---------------------------
# Content pages
# ---------------------------
if nav == "Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>RAVANA YT DOWNLOADER</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Fast • Clean • Professional</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Ravana is designed for students and creators to fetch YouTube media with clarity and control. Preview videos and playlists, pick exact resolutions or bitrates, download items individually with live progress, or grab the whole playlist as a ZIP. Please respect copyright and YouTube terms of service.</div>", unsafe_allow_html=True)
    st.markdown("<br><ul class='small-muted'><li>Supports video up to 4K (if available).</li><li>Audio selection from 64kbps to 360kbps.</li><li>Per-item download progress shows steps 10%,20%...100%.</li><li>Theme toggle: Dark (black+green) and Light (white+violet).</li></ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if nav == "About":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>About</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Created by D. Abhiram<br>Studying B.Sc. Computer Science, Sri Sathya Sai Institute of Higher Learning (SSSIHL), Nandigiri Campus.</div>", unsafe_allow_html=True)
    st.markdown("<br><div class='small-muted'>Ravana Downloader is built for clarity and classroom use: fast previews, precise quality selection and safe packaging. Always use responsibly.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------
# Downloader page layout
# ---------------------------
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Preview</div>", unsafe_allow_html=True)

    input_url = st.text_input("YouTube URL (video or playlist)", placeholder="https://www.youtube.com/watch?v=... or playlist URL")

    metadata = None
    playlist_entries = []
    detected_playlist = False

    if input_url and input_url.strip():
        try:
            meta = fetch_metadata(input_url)
            metadata = meta
            if meta.get("_type") == "playlist" and meta.get("entries"):
                detected_playlist = True
                # normalize entries: title, url, thumbnail, duration
                for e in meta.get("entries", []):
                    if not e:
                        continue
                    playlist_entries.append({
                        "title": e.get("title") or "Untitled",
                        "url": e.get("webpage_url") or e.get("url") or "",
                        "thumbnail": e.get("thumbnail"),
                        "duration": e.get("duration")
                    })
            else:
                detected_playlist = False
        except ModuleNotFoundError as me:
            st.error(str(me))
        except Exception as exc:
            st.error(f"Failed to fetch metadata: {exc}")

    if metadata and not detected_playlist:
        thumb = metadata.get("thumbnail")
        title = metadata.get("title") or "Unknown title"
        uploader = metadata.get("uploader") or ""
        duration = metadata.get("duration")
        if thumb:
            st.image(thumb, width=420)
        st.markdown(f"**{title}**")
        st.markdown(f"<div class='small-muted'>Channel: {uploader}</div>", unsafe_allow_html=True)
        if duration:
            st.markdown(f"<div class='small-muted'>Duration: {sec_to_hms(duration)}</div>", unsafe_allow_html=True)
    elif detected_playlist:
        st.markdown("<div class='small-muted'>Playlist detected. Use the table to download items individually or download the entire playlist from the right panel.</div>", unsafe_allow_html=True)
        st.markdown("<br>")
        # Table header
        st.markdown("<div style='display:flex; font-weight:700; padding:6px 0; color:var(--muted);'><div style='width:120px'>Thumbnail</div><div style='flex:1'>Title</div><div style='width:90px'>Duration</div><div style='width:140px'>Actions</div></div>", unsafe_allow_html=True)
        # Rows
        for idx, item in enumerate(playlist_entries):
            cols = st.columns([0.9, 3.2, 0.8, 1.6])
            with cols[0]:
                if item.get("thumbnail"):
                    st.image(item["thumbnail"], width=100)
                else:
                    st.write("")
            with cols[1]:
                st.markdown(f"<div style='font-weight:700'>{item.get('title')}</div>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div class='small-muted'>{sec_to_hms(item.get('duration'))}</div>", unsafe_allow_html=True)
            with cols[3]:
                # per-item controls
                dl_type = st.selectbox("Type", ["Video", "Audio"], key=f"type_{idx}")
                if dl_type == "Video":
                    res = st.selectbox("Res", ["144p","240p","360p","480p","720p","1080p","1440p","2160p (4K)"], key=f"res_{idx}", index=5)
                    quality_label = res.replace(" (4K)","")
                else:
                    ab = st.selectbox("Kbps", ["64kbps","128kbps","192kbps","320kbps","360kbps"], key=f"ab_{idx}", index=1)
                    quality_label = ab

                # status placeholders
                pbar = st.empty()
                status_lbl = st.empty()

                if st.button("Download item", key=f"dl_{idx}"):
                    item_url = item.get("url")
                    if not item_url:
                        st.error("Item URL not available.")
                    else:
                        out_folder = "downloads"
                        fname_prefix = (item.get("title") or f"item_{idx}").replace(" ", "_")[:120]
                        # choose format id from metadata (use overall metadata formats if available)
                        fmt_id = choose_format_id(metadata.get("formats", []), dl_type=="Video", quality_label)
                        if not fmt_id:
                            fmt_id = "bestvideo+bestaudio/best" if dl_type=="Video" else "bestaudio/best"

                        def report(pct):
                            pbar.progress(pct)
                            status_lbl.markdown(f"<div class='progress-label'>{pct}%</div>", unsafe_allow_html=True)

                        try:
                            downloaded_file = download_with_progress(item_url, fmt_id, out_folder, fname_prefix, "audio" if dl_type=="Audio" else "video", report)
                            st.success("Downloaded: " + os.path.basename(downloaded_file))
                            with open(downloaded_file, "rb") as fh:
                                st.download_button("Save file", data=fh.read(), file_name=os.path.basename(downloaded_file))
                        except ModuleNotFoundError as me:
                            st.error(str(me))
                        except Exception as e:
                            st.error(f"Download failed: {e}")

    else:
        st.markdown("<div class='small-muted'>Enter a YouTube URL to preview video or playlist.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Controls</div>", unsafe_allow_html=True)

    if not input_url or not metadata:
        st.markdown("<div class='small-muted'>Preview a URL on the left to enable controls (single video or playlist).</div>", unsafe_allow_html=True)
    else:
        # content override
        content_type = st.radio("Content", ["Single", "Playlist"], index=0 if metadata.get("_type")!="playlist" else 1, horizontal=True)
        is_playlist = content_type == "Playlist"

        dl_type = st.radio("Download Type", ["Video", "Audio"], horizontal=True)
        if dl_type == "Video":
            quality_choice = st.selectbox("Resolution", ["144p","240p","360p","480p","720p","1080p","1440p","2160p (4K)"], index=5)
            quality_label = quality_choice.replace(" (4K)","")
        else:
            quality_choice = st.selectbox("Audio bitrate", ["64kbps","128kbps","192kbps","320kbps","360kbps"], index=1)
            quality_label = quality_choice

        # ZIP option + name when playlist
        zip_output = False
        zip_name = None
        if is_playlist:
            zip_output = st.checkbox("Download full playlist as ZIP", value=True)
            if zip_output:
                zip_name = st.text_input("ZIP filename (no .zip)", value=(metadata.get("title") or "playlist").replace(" ", "_"))
                if not zip_name:
                    zip_name = (metadata.get("title") or "playlist").replace(" ", "_")
        else:
            zip_name = (metadata.get("title") or "download").replace(" ", "_")

        # choose format id for single or playlist-zip
        fmt_id = choose_format_id(metadata.get("formats", []), dl_type=="Video", quality_label)
        if not fmt_id:
            fmt_id = "bestvideo+bestaudio/best" if dl_type=="Video" else "bestaudio/best"

        if st.button("Download (single or playlist packaged)"):
            # single video direct download or playlist packaged using downloader.py
            if is_playlist and zip_output:
                # call external downloader (downloader.py) to produce zip buffer
                try:
                    from downloader import download_video_or_playlist
                except ModuleNotFoundError:
                    st.error("downloader.py not found or yt-dlp missing. Ensure downloader.py exists and yt-dlp is in requirements.")
                    st.stop()
                try:
                    st.info("Downloading playlist and creating ZIP. This may take some time.")
                    result = download_video_or_playlist(
                        url=input_url,
                        download_path="downloads",
                        download_type="audio" if dl_type=="Audio" else "video",
                        quality="Best" if dl_type=="Video" else "Best",
                        content_type="Playlist",
                        zip_output=True,
                        zip_filename=f"{zip_name}.zip"
                    )
                    # downloader returns (BytesIO, playlist_titles) per our downloader.py contract
                    if isinstance(result, tuple) and isinstance(result[0], io.BytesIO):
                        buf = result[0]
                        out_name = zip_name if zip_name.endswith(".zip") else f"{zip_name}.zip"
                        st.download_button("Download Playlist ZIP", data=buf.getvalue(), file_name=out_name)
                    elif isinstance(result, io.BytesIO):
                        out_name = zip_name if zip_name.endswith(".zip") else f"{zip_name}.zip"
                        st.download_button("Download Playlist ZIP", data=result.getvalue(), file_name=out_name)
                    else:
                        # fallback: if returns file list
                        paths = result if isinstance(result, list) else []
                        if paths:
                            mem = io.BytesIO()
                            with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
                                for p in paths:
                                    if os.path.exists(p):
                                        zf.write(p, arcname=os.path.basename(p))
                            mem.seek(0)
                            out_name = zip_name if zip_name.endswith(".zip") else f"{zip_name}.zip"
                            st.download_button("Download Playlist ZIP", data=mem.getvalue(), file_name=out_name)
                        else:
                            st.error("Downloader returned no files.")
                except Exception as e:
                    st.error(f"Playlist ZIP failed: {e}")

            else:
                # Single video download (or playlist single-mode: will try to download first item)
                # choose a filename prefix from title
                prefix = (metadata.get("title") or "download").replace(" ", "_")[:120]
                out_folder = "downloads"
                pbar = st.progress(0)
                lbl = st.empty()

                def report(p):
                    pbar.progress(p)
                    lbl.markdown(f"<div class='progress-label'>{p}%</div>", unsafe_allow_html=True)

                try:
                    downloaded_file = download_with_progress(input_url, fmt_id, out_folder, prefix, "audio" if dl_type=="Audio" else "video", report)
                    st.success("Downloaded: " + os.path.basename(downloaded_file))
                    with open(downloaded_file, "rb") as fh:
                        st.download_button("Save file", data=fh.read(), file_name=os.path.basename(downloaded_file))
                except ModuleNotFoundError as me:
                    st.error(str(me))
                except Exception as e:
                    st.error(f"Download failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# end spacing
st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
