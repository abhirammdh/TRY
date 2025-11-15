import streamlit as st
import os
from downloader import (
    get_video_info,
    download_video_or_playlist
)

st.set_page_config(page_title="Ravana YT Downloader", layout="wide")

# ----------------------- THEME ---------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

if st.sidebar.button("Toggle Theme"):
    toggle_theme()

dark = (st.session_state.theme == "dark")

BG = "#000000" if dark else "#ffffff"
TEXT = "#00ff66" if dark else "#5a2ca0"

st.markdown(f"""
<style>
body {{
    background-color: {BG};
    color: {TEXT};
}}
.stTextInput label {{
    color: {TEXT} !important;
}}
.stRadio label {{
    color: {TEXT} !important;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------- NAVIGATION -----------------------
menu = st.sidebar.radio("Menu", ["Home", "Download", "About"])

# ----------------------- HOME -----------------------
if menu == "Home":
    st.title("🔥 Ravana YT Downloader")
    st.write(f"""
Welcome to **Ravana YouTube Downloader** — the fastest & cleanest downloader.

### ⭐ Features:
- Best **4K video + audio**
- Best **M4A audio**
- Playlist support
- Thumbnail + Video details
- Light/Dark mode
- Clean UI and fast
""")

# ----------------------- ABOUT -----------------------
elif menu == "About":
    st.title("About")

    st.write("""
### Created by **D. Abhiram**

B.Sc Computer Science  
Sri Sathya Sai Institute of Higher Learning (SSSIHL), Nandigama Campus  

Made with ❤️ for students & creators who want easy and fast downloading.
""")

# ----------------------- DOWNLOAD -----------------------
elif menu == "Download":
    st.title("YouTube Downloader")

    url = st.text_input("Enter YouTube Video / Playlist URL:")

    if url.strip() != "":
        with st.spinner("Fetching video info..."):
            try:
                info = get_video_info(url)
            except:
                st.error("Invalid URL or unable to fetch details.")
                st.stop()

        # ----------- THUMBNAIL & DETAILS ------------
        col1, col2 = st.columns([1, 2])

        with col1:
            if info["thumbnail"]:
                st.image(info["thumbnail"], width=300)

        with col2:
            st.subheader(info["title"])
            st.write(f"**Channel:** {info['channel']}")
            st.write(f"**Views:** {info['views']}")
            st.write(f"**Duration:** {info['duration']} seconds")
            st.write(f"**Uploaded:** {info['upload_date']}")

        st.markdown("---")

        # ----------- Mode Selection ------------
        mode = st.radio("Choose Download Mode:", ["Video", "Audio"])

        # ----------- Download Button ------------
        if st.button("Download Now"):
            with st.spinner("Downloading... Please wait"):
                try:
                    files = download_video_or_playlist(
                        url,
                        mode="video" if mode == "Video" else "audio"
                    )
                except Exception as e:
                    st.error(f"Download failed: {e}")
                    st.stop()

            st.success("Download Complete ✔️")

            # Return all files
            for f in files:
                if os.path.exists(f):
                    with open(f, "rb") as file:
                        st.download_button(
                            label=f"Download {os.path.basename(f)}",
                            data=file,
                            file_name=os.path.basename(f),
                            mime="application/octet-stream"
                        )
                else:
                    st.warning(f"File not found: {f}")
