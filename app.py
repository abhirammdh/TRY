import streamlit as st
from downloader import (
    download_video,
    download_audio,
    get_playlist_items
)
import requests
from io import BytesIO
import zipfile


# Page Setup
st.set_page_config(page_title="Ravana YT Downloader", layout="wide")

# Theme Toggle
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

if st.session_state.theme == "dark":
    bg = "#000000"
    text = "#00ff66"
else:
    bg = "#ffffff"
    text = "#6c33ff"

# Custom CSS (clean modern UI)
st.markdown(f"""
    <style>
        body {{
            background-color: {bg};
            color: {text};
        }}
        .stButton>button {{
            background: {text};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
        }}
    </style>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Home", "Download", "About"])

if st.sidebar.button("Toggle Theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


# ---------------- HOME ----------------
if page == "Home":
    st.title("🔥 Ravana YT Downloader")
    st.write("""
    Welcome to **Ravana YT Downloader**

    ### ⭐ Features
    - Download **Video (240p → 4K)**  
    - Download **Audio (60kbps → 360kbps)**  
    - Playlist item-wise download  
    - Thumbnail preview  
    - ZIP download  
    - Dark/Light themes  
    """)


# ---------------- ABOUT ----------------
if page == "About":
    st.title("About Developer")
    st.write("""
    **Created by:** D. Abhiram  
    B.Sc Computer Science, **SSSIHL Nandigama Campus**

    A clean, fast and modern downloader built for students & creators ❤️
    """)


# ---------------- DOWNLOAD ----------------
if page == "Download":
    st.title("Download YouTube Video / Audio")

    url = st.text_input("Enter YouTube URL")

    if url:
        # Thumbnail
        try:
            if "v=" in url:
                vid = url.split("v=")[1][:11]
                st.image(f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg", width=500)
        except:
            st.warning("Thumbnail not available.")

        mode = st.radio("Select Mode", ["Video", "Audio", "Playlist"])

        # VIDEO MODE
        if mode == "Video":
            q = st.selectbox("Select Video Quality", [
                "240p","360p","480p","720p","1080p","1440p (2K)","2160p (4K)"
            ])
            if st.button("Download Video"):
                file = download_video(url, q)
                if file:
                    with open(file, "rb") as f:
                        st.download_button("Download File", f, file_name=file)
                else:
                    st.error("Download failed.")

        # AUDIO MODE
        elif mode == "Audio":
            q = st.selectbox("Select Audio Quality", [
                "60kbps","128kbps","192kbps","256kbps","320kbps","360kbps"
            ])
            if st.button("Download Audio"):
                file = download_audio(url, q)
                if file:
                    with open(file, "rb") as f:
                        st.download_button("Download File", f, file_name=file)
                else:
                    st.error("Download failed.")

        # PLAYLIST MODE
        else:
            st.subheader("Playlist Videos")
            items = get_playlist_items(url)

            for i, video in enumerate(items):
                st.write(f"**{i+1}. {video['title']}**")
                col1, col2 = st.columns([4,1])
                with col2:
                    if st.button("Download", key=f"d{i}"):
                        f = download_video(video["url"], "720p")
                        with open(f, "rb") as fp:
                            st.download_button("Save", fp, file_name=f"{video['title']}.mp4", key=f"s{i}")


