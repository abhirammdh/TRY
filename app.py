
import streamlit as st
import os
import time
import io
import zipfile
from downloader import download_video_or_playlist

# ------------------- THEME CSS (SMOOTH & MINIMALIST) -------------------
def load_theme(dark=True):
    if dark:
        st.markdown("""
        <style>
        body { 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); 
            color: #e0e0e0; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        .glass {
            background: rgba(255,255,255,0.02);
            backdrop-filter: blur(20px);
            padding: 28px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .title {
            font-size: 40px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 30px;
            text-align: center;
            letter-spacing: -0.5px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(79,70,229,0.3);
            width: 100%;
            text-align: center;
            height: 50px;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(79,70,229,0.4);
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        }
        .fade-in {
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #e0e0e0;
            padding: 12px;
            width: 100%;
            height: 45px;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
        }
        .preview-section {
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            animation: fadeIn 1s ease-out;
        }
        .block-container {
            padding-top: 2rem;
        }
        [data-testid="column"] {
            padding: 0 8px;
        }
        .stSuccess > div > div {
            background: rgba(34,197,94,0.2);
            border-radius: 10px;
            border-left: 4px solid #22c55e;
        }
        .stError > div > div {
            background: rgba(239,68,68,0.2);
            border-radius: 10px;
            border-left: 4px solid #ef4444;
        }
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body { 
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
            color: #334155; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        .glass {
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(20px);
            padding: 28px;
            border-radius: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .title {
            font-size: 40px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 30px;
            text-align: center;
            letter-spacing: -0.5px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(79,70,229,0.3);
            width: 100%;
            text-align: center;
            height: 50px;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(79,70,229,0.4);
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        }
        .fade-in {
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid rgba(0,0,0,0.05);
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(0,0,0,0.1);
            border-radius: 10px;
            color: #334155;
            padding: 12px;
            width: 100%;
            height: 45px;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
        }
        .preview-section {
            background: rgba(255,255,255,0.8);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            animation: fadeIn 1s ease-out;
        }
        .block-container {
            padding-top: 2rem;
        }
        [data-testid="column"] {
            padding: 0 8px;
        }
        .stSuccess > div > div {
            background: rgba(34,197,94,0.2);
            border-radius: 10px;
            border-left: 4px solid #22c55e;
        }
        .stError > div > div {
            background: rgba(239,68,68,0.2);
            border-radius: 10px;
            border-left: 4px solid #ef4444;
        }
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
        }
        </style>
        """, unsafe_allow_html=True)

# ------------------- YOUTUBE INFO FETCH -------------------
def get_info(url):
    try:
        import yt_dlp
        ydl_opts = {"quiet": True, "skip_download": True, "ignoreerrors": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        st.error(f"Preview failed: {str(e)}")
        return None

# ------------------- PAGES -------------------
st.set_page_config(page_title="RAVANA YT DOWNLOADER", layout="wide", initial_sidebar_state="collapsed")
menu = st.sidebar.radio("Menu", ["Home", "About"])
theme_switch = st.sidebar.toggle("Dark Theme", value=True)
load_theme(theme_switch)

if menu == "About":
    st.markdown("<div class='title'>About</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Features:**")
        st.write("• High-quality video downloads")
        st.write("• Playlist ZIP export")
        st.write("• Smooth progress tracking")
    with col2:
        st.write("**By:** Devulapalli Abhiram (RAVANA)")
        st.write("**Tech:** Streamlit + yt-dlp")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ------------------- HOME -------------------
st.markdown("<div class='title'>Ravana YT Downloader</div>", unsafe_allow_html=True)

st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
st.header("Enter URL")
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
with col2:
    preview_clicked = st.button("Preview")

col1, col2 = st.columns(2)
with col1:
    mode = st.selectbox("Mode", ["Video", "Playlist"])
with col2:
    video_quality = st.selectbox("Quality", ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p (2K)", "2160p (4K)"])
st.markdown('</div>', unsafe_allow_html=True)

# Preview
if url and preview_clicked:
    with st.spinner("Loading preview..."):
        info = get_info(url)
    if info:
        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
        st.header("Preview")
        col1, col2 = st.columns([1, 3])
        with col1:
            if "thumbnail" in info:
                st.image(info["thumbnail"], use_column_width=True)
        with col2:
            st.subheader(info.get("title", "N/A"))
            st.write(f"**Duration:** {info.get('duration', 'N/A')}s")
            st.write(f"**Views:** {info.get('view_count', 'N/A'):,}")
        
        if mode == "Playlist" and "entries" in info:
            st.subheader("Playlist (First 5)")
            for i, e in enumerate(info["entries"][:5], 1):
                st.write(f"{i}. {e.get('title', 'N/A')}")
            if len(info["entries"]) > 5:
                st.write("...and more")
        st.markdown('</div>', unsafe_allow_html=True)

# Download
st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
st.header("Download")
if st.button("Start Download"):
    if not url:
        st.error("Enter a URL!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                p_str = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', 'N/A')
                status_text.text(f"Downloading: {p_str} | {speed}")
                if p_str != '0%':
                    try:
                        p = float(p_str.replace('%', '')) / 100
                        progress_bar.progress(p)
                    except:
                        pass
            elif d['status'] == 'finished':
                status_text.text("Finishing up...")
        
        zip_name = "downloads"
        if mode == "Playlist":
            zip_name = st.text_input("ZIP Name", value="playlist", key="zip")
        
        result, titles, thumbnails = download_video_or_playlist(
            url=url,
            download_type="video",
            quality=video_quality,
            content_type=mode,
            zip_output=(mode == "Playlist"),
            zip_filename=f"{zip_name}.zip",
            progress_hook=progress_hook
        )
        
        progress_bar.progress(1.0)
        status_text.text("Ready!")
        
        if result is None:
            st.error("Download failed. Check URL.")
        else:
            st.success("Success!")
            st.subheader("Items:")
            for i, t in enumerate(titles, 1):
                st.write(f"{i}. {t}")
                # Show thumbnail if available
                if thumbnails and i <= len(thumbnails) and thumbnails[i-1]:
                    st.image(thumbnails[i-1], width=200, caption=t)
            
            if mode == "Playlist" and isinstance(result, bytes):
                st.download_button("Download ZIP", result, f"{zip_name}.zip", "application/zip", use_container_width=True)
            elif isinstance(result, list):
                for fp in result:
                    with open(fp, "rb") as f:
                        fn = os.path.basename(fp)
                        st.download_button(f"Download {fn}", f, fn, use_container_width=True)
            else:
                with open(result, "rb") as f:
                    fn = os.path.basename(result)
                    st.download_button("Download Video", f, fn, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8;'>© 2025 Ravana | Smooth Downloads</div>", unsafe_allow_html=True)
