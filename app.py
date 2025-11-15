import streamlit as st
import os
from downloader import download_video_or_playlist


st.set_page_config(page_title="Ravana YT Downloader", layout="wide")

# ---------------------------------------------------------
# THEME SWITCHER
# ---------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# COLORS
if st.session_state.theme == "dark":
    BG = "#000000"
    TEXT = "#00ff66"
else:
    BG = "#ffffff"
    TEXT = "#6a0dad"

st.markdown(f"""
<style>
body {{
    background-color: {BG};
    color: {TEXT};
}}
.stButton>button {{
    background-color: transparent;
    color: {TEXT};
    border: 2px solid {TEXT};
    padding: 10px 20px;
    border-radius: 10px;
    transition: 0.3s;
}}
.stButton>button:hover {{
    transform: scale(1.05);
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("⚙ Settings")
if st.sidebar.button("Toggle Theme"):
    toggle_theme()

page = st.sidebar.radio("Navigate", ["Home", "Download", "History", "About"])


# ---------------------------------------------------------
# GLOBAL HISTORY
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if page == "Home":
    st.title("🔥 Ravana YT Downloader")
    st.write("""
    Welcome to **Ravana YouTube Downloader**, the most powerful downloader built with:

    ✔ Fast video/audio downloads  
    ✔ Up to **4K MP4**  
    ✔ Pure **M4A audio**  
    ✔ Download playlist fully  
    ✔ Beautiful dark/light themes  
    ✔ Full progress bar  
    ✔ No cookies required  
    """)


# ---------------------------------------------------------
# DOWNLOAD PAGE
# ---------------------------------------------------------
if page == "Download":
    st.title("🎬 Download YouTube Video / Audio")

    url = st.text_input("Enter YouTube Link:")
    mode = st.radio("Select Mode:", ["Video", "Audio"])

    if mode == "Video":
        quality = st.selectbox(
            "Video Quality:",
            ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        )
    else:
        quality = "audio"   # audio has no quality dropdown

    if st.button("Start Download"):
        if not url.strip():
            st.error("Please enter a link")
        else:
            with st.spinner("Downloading… Please wait…"):
                files = download_video_or_playlist(
                    url,
                    quality=quality if mode == "Video" else "720p",
                    mode="video" if mode == "Video" else "audio"
                )

            st.success("Download Completed!")

            for f in files:
                if os.path.exists(f):
                    with open(f, "rb") as data:
                        st.download_button(
                            label=f"Download {os.path.basename(f)}",
                            data=data,
                            file_name=os.path.basename(f)
                        )

            # SAVE HISTORY
            st.session_state.history.append({
                "url": url,
                "mode": mode,
                "files": files
            })


# ---------------------------------------------------------
# HISTORY PAGE
# ---------------------------------------------------------
if page == "History":
    st.title("📜 Download History")

    if len(st.session_state.history) == 0:
        st.info("No downloads yet.")
    else:
        for item in st.session_state.history:
            st.write(f"**URL:** {item['url']}")
            st.write(f"Mode: {item['mode']}")
            for f in item['files']:
                st.write(f"📁 {f}")
            st.markdown("---")


# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------
if page == "About":
    st.title("👨‍💻 About Developer")
    st.write("""
    **Created by:** D. Abhiram  
    **Studying:** B.Sc Computer Science  
    **College:** SSSIHL, Nandigama Campus  

    Ravana Downloader is made to be:
    - Fast  
    - Clean  
    - Professional  
    - Student-friendly  
    """)







