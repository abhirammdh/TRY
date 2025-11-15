import streamlit as st
import os
import time
import io
import zipfile
from downloader import download_video_or_playlist

# ------------------- THEME CSS (ULTIMATE: MINIMALIST, PROFESSIONAL ALIGNMENT) -------------------
def load_theme(dark=True):
    if dark:
        st.markdown("""
        <style>
        /* Global Styles: Clean & Modern */
        body { 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); 
            color: #e0e0e0; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        
        /* Subtle Glassmorphism */
        .glass {
            background: rgba(255,255,255,0.02);
            backdrop-filter: blur(20px);
            padding: 28px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        
        /* Title: Bold & Centered */
        .title {
            font-size: 40px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 30px;
            text-align: center;
            letter-spacing: -0.5px;
        }
        
        /* Buttons: Sleek & Full-Width */
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
        
        /* Subtle Fade-in */
        .fade-in {
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Sidebar: Refined */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Inputs & Selects: Clean Borders */
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
        
        /* Preview Section */
        .preview-section {
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            animation: fadeIn 1s ease-out;
        }
        
        /* Columns: Perfect Spacing */
        .block-container {
            padding-top: 2rem;
        }
        [data-testid="column"] {
            padding: 0 8px;
        }
        
        /* Success/Error: Styled */
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
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        /* Light Theme: Clean & Modern */
        body { 
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
            color: #334155; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        
        /* Subtle Glassmorphism */
        .glass {
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(20px);
            padding: 28px;
            border-radius: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Title: Bold & Centered */
        .title {
            font-size: 40px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 30px;
            text-align: center;
            letter-spacing: -0.5px;
        }
        
        /* Buttons: Sleek & Full-Width */
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
        
        /* Subtle Fade-in */
        .fade-in {
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Sidebar: Refined */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid rgba(0,0,0,0.05);
        }
        
        /* Inputs & Selects: Clean Borders */
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
        
        /* Preview Section */
        .preview-section {
            background: rgba(255,255,255,0.8);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            animation: fadeIn 1s ease-out;
        }
        
        /* Columns: Perfect Spacing */
        .block-container {
            padding-top: 2rem;
        }
        [data-testid="column"] {
            padding: 0 8px;
        }
        
        /* Success/Error: Styled */
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
st.set_page_config(
    page_title="RAVANA YT DOWNLOADER", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
menu = st.sidebar.radio("Menu", ["Home", "About"])
theme_switch = st.sidebar.toggle("Dark Theme", value=True)
load_theme(theme_switch)

if menu == "About":
    st.markdown("<div class='title'>About Ravana YT Downloader</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Features:**")
        st.write("• High-quality video downloads (144p–4K)")
        st.write("• Audio extraction (64–320kbps MP3)")
        st.write("• Playlist support with ZIP export")
        st.write("• Metadata preview & fast processing")
    with col2:
        st.write("**Created by:**")
        st.write("Devulapalli Abhiram (RAVANA)")
        st.write("**Tech Stack:**")
        st.write("• Streamlit • yt-dlp • FFmpeg")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ------------------- HOME PAGE -------------------
st.markdown("<div class='title'>Ravana YT Downloader</div>", unsafe_allow_html=True)

# Input Section
st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
st.header("Enter Details")
url_col1, url_col2 = st.columns([3, 1])
with url_col1:
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", help="Paste a single video or playlist URL")
with url_col2:
    preview_clicked = st.button("Preview", key="preview_btn")

options_col1, options_col2, options_col3 = st.columns(3)
with options_col1:
    mode = st.selectbox("Mode", ["Video", "Audio", "Playlist"], help="Choose download type")
with options_col2:
    video_quality = st.selectbox("Video Quality", ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p (2K)", "2160p (4K)"])
with options_col3:
    audio_quality = st.selectbox("Audio Quality (kbps)", ["64", "128", "192", "256", "320"])

st.markdown('</div>', unsafe_allow_html=True)

# Preview Section
if url and preview_clicked:
    with st.spinner("Fetching details..."):
        info = get_info(url)
    if info:
        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
        st.header("Preview")
        preview_col1, preview_col2 = st.columns([1, 3])
        with preview_col1:
            st.image(info.get("thumbnail"), use_column_width=True)
        with preview_col2:
            st.subheader(info.get("title", "N/A"))
            st.write(f"**Duration:** {info.get('duration', 'N/A')} seconds")
            st.write(f"**Views:** {info.get('view_count', 'N/A'):,}")
            st.write(f"**Uploader:** {info.get('uploader', 'N/A')}")
        
        # Playlist Preview
        if mode == "Playlist" and "entries" in info:
            st.subheader("Playlist Contents (First 5)")
            for i, entry in enumerate(info["entries"][:5], 1):
                st.write(f"{i}. {entry.get('title', 'N/A')}")
            if len(info["entries"]) > 5:
                st.write(f"... and {len(info['entries']) - 5} more")
        st.markdown('</div>', unsafe_allow_html=True)

# Download Section
st.markdown('<div class="glass fade-in">', unsafe_allow_html=True)
st.header("Download")
if st.button("Start Download", key="download_btn"):
    if not url:
        st.error("Please enter a YouTube URL first.")
    else:
        with st.spinner("Processing your request..."):
            zip_name = "playlist"
            if mode == "Playlist":
                zip_name = st.text_input("ZIP Filename", value="playlist_downloads", key="zip_name_input")
            
            download_type = "video" if mode in ["Video", "Playlist"] else "audio"
            quality = video_quality if mode != "Audio" else audio_quality
            
            result, titles = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=mode,
                zip_output=(mode == "Playlist"),
                zip_filename=f"{zip_name}.zip"
            )
            
            if result is None:
                st.error("Download failed. Please check the URL and try again.")
            else:
                st.success("Download prepared successfully!")
                
                # Titles List
                st.subheader("Downloaded Items")
                for i, title in enumerate(titles, 1):
                    st.write(f"{i}. {title}")
                
                # Download Buttons
                if mode == "Playlist" and isinstance(result, bytes):
                    st.download_button(
                        "Download ZIP Archive",
                        data=result,
                        file_name=f"{zip_name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                elif isinstance(result, list):
                    for file_path in result:
                        with open(file_path, "rb") as f:
                            fname = os.path.basename(file_path)
                            st.download_button(
                                f"Download {fname}",
                                data=f,
                                file_name=fname,
                                use_container_width=True
                            )
                else:
                    with open(result, "rb") as f:
                        label = "Download Video" if mode == "Video" else "Download Audio"
                        st.download_button(
                            label,
                            data=f,
                            file_name=os.path.basename(result),
                            use_container_width=True
                        )
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 14px; color: #94a3b8;'>© 2025 Ravana YT Downloader | Built with Streamlit</div>", unsafe_allow_html=True)
