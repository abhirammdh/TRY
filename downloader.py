import streamlit as st
import os
from downloader import download_video_or_playlist

st.set_page_config(page_title="Ravana Downloader", layout="centered")

st.title("🔥 Ravana YouTube Downloader")

# --- Input UI ---
url = st.text_input("Enter YouTube Video or Playlist URL")

col1, col2 = st.columns(2)

with col1:
    mode = st.selectbox("Choose Type", ["video", "audio"])

with col2:
    quality = st.selectbox("Video Quality", ["360p", "480p", "720p", "1080p"])

# Button
if st.button("Download"):
    if not url.strip():
        st.error("Please enter a valid YouTube URL")
    else:
        with st.spinner("Downloading... please wait ⚡"):
            try:
                files = download_video_or_playlist(url, quality, mode)

                st.success("🎉 Download Completed!")

                # Show download buttons for each file
                for file in files:
                    if os.path.exists(file):
                        st.download_button(
                            label=f"Download {os.path.basename(file)}",
                            data=open(file, "rb"),
                            file_name=os.path.basename(file)
                        )
                    else:
                        st.warning("File not found after download.")

            except Exception as e:
                st.error(f"❌ Error: {e}")

