import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Ravana yt downloader", layout="centered")

# ---------------------------------------
# Navigation
# ---------------------------------------
page = st.sidebar.radio("Navigation", ["Home", "Downloader"])

# ---------------------------------------
# Home Section
# ---------------------------------------
if page == "Home":
    st.title("🔥 Ravana YouTube Downloader")
    st.write("""
    Welcome to **Ravana Downloader**!  
    Fast, simple, and powerful YouTube video/audio downloader.
    
    ### Features:
    - Download YouTube **Videos**
    - Download **Audio Only**
    - Supports private videos using **cookies.txt**
    - Fast & Clean UI  
    """)
    st.info("Use the sidebar to open the Downloader section.")

# ---------------------------------------
# Downloader Section
# ---------------------------------------
if page == "Downloader":
    st.title("📥 YouTube Video / Audio Downloader")

    url = st.text_input("Enter YouTube Video URL")

    content_type = st.radio("Select Type", ["Video", "Audio"])
    
    st.write("Optional: Upload cookies.txt (Fixes 'Sign in to confirm you’re not a bot')")
    cookies_file = st.file_uploader("Upload cookies.txt", type=["txt"])

    # Quality options
    if content_type == "Video":
        quality = st.selectbox(
            "Select Quality",
            ["best", "bestvideo+bestaudio", "worst"]
        )
    else:
        quality = st.selectbox(
            "Select Audio Quality",
            ["140 (m4a)", "best", "worst"]
        )

    def download_video(url, quality, cookies=None):
        ydl_opts = {
            "format": quality,
            "outtmpl": "%(title)s.%(ext)s",
            "noplaylist": True,
        }

        if cookies:
            ydl_opts["cookiefile"] = cookies

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    if st.button("Download"):
        if not url:
            st.error("Please enter a valid video URL.")
        else:
            st.info("Downloading... Please wait.")

            cookie_path = None
            if cookies_file:
                cookie_path = "cookies.txt"
                with open(cookie_path, "wb") as f:
                    f.write(cookies_file.read())

            try:
                output = download_video(url, quality, cookie_path)
                st.success("Download finished!")

                with open(output, "rb") as f:
                    st.download_button(
                        "Click to Download File",
                        data=f,
                        file_name=os.path.basename(output)
                    )

            except Exception as e:
                st.error(f"❌ Error: {e}")

            if cookie_path and os.path.exists(cookie_path):
                os.remove(cookie_path)

