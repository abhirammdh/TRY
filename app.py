
import streamlit as st
import yt_dlp
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Ravana YT Downloader",
    layout="centered",
)

# -------------------- CUSTOM CSS ---------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

* { font-family: 'Poppins', sans-serif !important; }

body {
    background: linear-gradient(135deg, #0f0f0f, #1c1c1c);
    color: white;
}

.css-ffhzg2, .css-1v0mbdj {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px) !important;
    border-radius: 18px !important;
    padding: 20px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

.sidebar .sidebar-content {
    background: #121212 !important;
}

/* Button Styling */
button {
    border-radius: 10px !important;
    transition: 0.3s ease-in-out;
}
button:hover {
    transform: scale(1.03);
}

/* Title */
h1 {
    color: #e03131 !important;
    text-align: center;
    font-weight: 700 !important;
}

/* Card */
.glass-card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.markdown("<h1>RAVANA YT DOWNLOADER</h1>", unsafe_allow_html=True)
st.write("##### Professional YouTube Video & Playlist Downloader")

st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

# -------------------- NAVIGATION --------------------
menu = st.radio(
    "Choose Mode",
    ["Single Video", "Playlist"],
    horizontal=True
)

# -------------------- PROGRESS HANDLER --------------------
progress_bar = st.progress(0)
status_text = st.empty()

def progress_hook(d):
    if d['status'] == 'downloading':
        if "total_bytes" in d:
            percent = d['downloaded_bytes'] / d['total_bytes']
            progress_bar.progress(percent)
            status_text.text(f"Downloading: {int(percent*100)}%")
    elif d['status'] == 'finished':
        status_text.text("Processing video...")

# -------------------- DOWNLOAD FUNCTION --------------------
def download_youtube(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "progress_hooks": [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, "Download completed successfully."
    except Exception as e:
        return False, "Error: " + str(e)

# -------------------- SINGLE VIDEO --------------------
if menu == "Single Video":
    st.subheader("Download Single Video")

    url = st.text_input("Enter YouTube Video URL")
    folder = st.text_input("Folder Name", "downloads/video")

    if st.button("Download Video"):
        if url:
            st.info("Starting download...")
            success, msg = download_youtube(url, folder)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# -------------------- PLAYLIST --------------------
elif menu == "Playlist":
    st.subheader("Download Playlist")

    url = st.text_input("Enter Playlist URL")
    folder = st.text_input("Folder Name", "downloads/playlist")

    if st.button("Download Playlist"):
        if url:
            st.info("Starting playlist download...")
            success, msg = download_youtube(url, folder)
            if success:
                st.success(msg)
            else:
                st.error(msg)

st.markdown("</div>", unsafe_allow_html=True)


