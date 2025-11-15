import streamlit as st
import os
import time
import io
import zipfile
from downloader import download_video_or_playlist

# ------------------- THEME CSS (REFINED: NO GLOW, CLEAN ALIGNMENT) -------------------
def load_theme(dark=True):
    if dark:
        st.markdown("""
        <style>
        /* Global Styles */
        body { 
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); 
            color: #00ffcc; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Glassmorphism Container */
        .glass {
            backdrop-filter: blur(14px);
            background: rgba(0,255,200,0.08);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid rgba(0,255,200,0.25);
            box-shadow: 0 8px 32px rgba(0,255,200,0.1);
            transition: all 0.3s ease-in-out;
        }
        .glass:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,255,200,0.15);
        }
        
        /* Title: Clean, No Glow */
        .title {
            font-size: 36px;
            font-weight: 800;
            color: #00ffcc;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Professional Button Styles: No Pulse/Glow */
        .stButton > button {
            background: linear-gradient(135deg, #00ffcc 0%, #0099aa 100%);
            color: #000;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0,255,200,0.2);
            position: relative;
            overflow: hidden;
            width: 100%;
            text-align: center;
        }
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,255,200,0.3);
            background: linear-gradient(135deg, #00ccaa 0%, #007799 100%);
        }
        .stButton > button:active {
            transform: translateY(-1px) scale(1);
            box-shadow: 0 4px 15px rgba(0,255,200,0.2);
        }
        
        /* Fade-in Animation for Elements */
        .fade-in {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Sidebar Enhancements */
        .css-1d391kg {  /* Sidebar */
            background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(26,26,26,0.8) 100%);
            border-right: 1px solid rgba(0,255,200,0.1);
        }
        
        /* Input Field Styling */
        .stTextInput > div > div > input {
            background: rgba(0,255,200,0.05);
            border: 1px solid rgba(0,255,200,0.2);
            border-radius: 8px;
            color: #00ffcc;
            padding: 10px;
            transition: border 0.3s ease;
            width: 100%;
        }
        .stTextInput > div > div > input:focus {
            border-color: #00ffcc;
            box-shadow: 0 0 10px rgba(0,255,200,0.1);
        }
        
        /* Selectbox Styling */
        .stSelectbox > div > div > select {
            background: rgba(0,255,200,0.05);
            border: 1px solid rgba(0,255,200,0.2);
            border-radius: 8px;
            color: #00ffcc;
            width: 100%;
        }
        
        /* Thumbnail and Info Fade-in */
        .preview-section {
            animation: fadeIn 1s ease-out;
        }
        
        /* Improved Alignment for Columns */
        .stColumns > div {
            padding: 0 5px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        /* Global Styles (Light Theme) */
        body { 
            background: linear-gradient(135deg, #f0f0f0 0%, #ffffff 100%); 
            color: #6a00ff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Glassmorphism Container */
        .glass {
            backdrop-filter: blur(14px);
            background: rgba(106,0,255,0.05);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid rgba(106,0,255,0.25);
            box-shadow: 0 8px 32px rgba(106,0,255,0.1);
            transition: all 0.3s ease-in-out;
        }
        .glass:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(106,0,255,0.15);
        }
        
        /* Title: Clean, No Glow */
        .title {
            font-size: 36px;
            font-weight: 800;
            color: #6a00ff;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Professional Button Styles: No Pulse/Glow */
        .stButton > button {
            background: linear-gradient(135deg, #6a00ff 0%, #9d4edd 100%);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(106,0,255,0.2);
            position: relative;
            overflow: hidden;
            width: 100%;
            text-align: center;
        }
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(106,0,255,0.3);
            background: linear-gradient(135deg, #5a00e6 0%, #8d3acc 100%);
        }
        .stButton > button:active {
            transform: translateY(-1px) scale(1);
            box-shadow: 0 4px 15px rgba(106,0,255,0.2);
        }
        
        /* Fade-in Animation for Elements */
        .fade-in {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Sidebar Enhancements */
        .css-1d391kg {  /* Sidebar */
            background: linear-gradient(180deg, rgba(240,240,240,0.9) 0%, rgba(255,255,255,0.9) 100%);
            border-right: 1px solid rgba(106,0,255,0.1);
        }
        
        /* Input Field Styling */
        .stTextInput > div > div > input {
            background: rgba(106,0,255,0.05);
            border: 1px solid rgba(106,0,255,0.2);
            border-radius: 8px;
            color: #6a00ff;
            padding: 10px;
            transition: border 0.3s ease;
            width: 100%;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6a00ff;
            box-shadow: 0 0 10px rgba(106,0,255,0.1);
        }
        
        /* Selectbox Styling */
        .stSelectbox > div > div > select {
            background: rgba(106,0,255,0.05);
            border: 1px solid rgba(106,0,255,0.2);
            border-radius: 8px;
            color: #6a00ff;
            width: 100%;
        }
        
        /* Thumbnail and Info Fade-in */
        .preview-section {
            animation: fadeIn 1s ease-out;
        }
        
        /* Improved Alignment for Columns */
        .stColumns > div {
            padding: 0 5px;
        }
        </style>
        """, unsafe_allow_html=True)

# ------------------- YOUTUBE INFO FETCH -------------------
def get_info(url):
    try:
        import yt_dlp
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except:
        return None

# ------------------- STREAMLIT PAGES -------------------
st.set_page_config(page_title="RAVANA YT DOWNLOADER", layout="wide")
menu = st.sidebar.radio("Menu", ["Home", "About"])
theme_switch = st.sidebar.toggle("Dark Theme", value=True)
load_theme(theme_switch)

if menu == "About":
    st.markdown("<div class='title'>About</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
    st.write("""
    **Ravana YT Downloader**
    - Built for high-quality YouTube downloads
    - Created by **Devulapalli Abhiram (RAVANA)**
    - Supports: video (144p–4K), audio (64–320kbps), playlists, ZIP, metadata
    - Modern UI with glassmorphism + animations
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ------------------- HOME PAGE -------------------
st.markdown("<div class='title'>RAVANA YT DOWNLOADER</div>", unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("Enter YouTube URL", placeholder="Paste your YouTube link here...")
    with col2:
        if st.button("Preview", key="preview_btn"):
            time.sleep(0.5)  # Simulate loading for animation feel
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mode = st.selectbox("Mode", ["Video", "Audio", "Playlist"])
    with col2:
        video_quality = st.selectbox("Video Quality",
            ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p (2K)", "2160p (4K)"]
        )
    with col3:
        audio_quality = st.selectbox("Audio Quality (MP3 kbps)", ["64", "128", "192", "256", "320"])

    # Correct yt-dlp format mappings (for reference, used in downloader.py)
    format_map = {
        "144p": "bestvideo[height<=144]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "1440p (2K)": "bestvideo[height<=1440]+bestaudio/best",
        "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best"
    }
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------- PREVIEW -------------------
if url:
    info = get_info(url)
    if info:
        st.markdown('<div class="preview-section glass">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(info.get("thumbnail"), width=320, use_column_width=True)
        with col2:
            st.write(f"**Title:** {info.get('title')}")
            st.write(f"**Duration:** {info.get('duration', 'N/A')}s")
            st.write(f"**Views:** {info.get('view_count', 'N/A'):,}")
        
        # Playlist videos
        if mode == "Playlist" and "entries" in info:
            st.subheader("Playlist Preview")
            for i, v in enumerate(info["entries"][:5], start=1):  # Show first 5
                st.write(f"{i}. {v.get('title', 'N/A')}")
                if i == 5:
                    st.write("... and more")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------- DOWNLOAD -------------------
if st.button("Download Now", help="Click to start downloading!", key="download_btn"):
    if not url:
        st.warning("Enter a URL first!")
    else:
        with st.spinner("Downloading... Please wait while we fetch your content."):
            zip_name = "playlist"  # Default value to avoid NameError
            if mode == "Video":
                download_type = "video"
                qual = video_quality
            elif mode == "Audio":
                download_type = "audio"
                qual = audio_quality
            elif mode == "Playlist":
                download_type = "video"  # Default; add toggle for audio if needed
                qual = video_quality
                zip_name = st.text_input("ZIP File Name", value="playlist", key="zip_name")
            
            result, titles = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=qual,
                content_type=mode,
                zip_output=(mode == "Playlist"),
                zip_filename=f"{zip_name}.zip"
            )
            
            if result is None:
                st.error("Download failed! Check URL or try again.")
            else:
                st.success("Download ready!")
                # Show titles with fade-in
                st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                st.subheader("Downloaded Items:")
                for title in titles:
                    st.write(f"• {title}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download buttons with professional styling
                if mode == "Playlist" and isinstance(result, bytes):
                    # ZIP download
                    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                    st.download_button(
                        "Download Playlist ZIP",
                        data=result,
                        file_name=zip_name + ".zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Single or non-zip playlist
                    if isinstance(result, list):
                        for file_path in result:
                            with open(file_path, "rb") as f:
                                fname = os.path.basename(file_path)
                                st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                                st.download_button(f"{fname}", f, file_name=fname, use_container_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # Single file
                        with open(result, "rb") as f:
                            st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                            label = "Download Video" if mode == "Video" else "Download Audio"
                            st.download_button(label, f, file_name=os.path.basename(result), use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Powered by RAVANA | High-Quality Downloads</div>", unsafe_allow_html=True)
