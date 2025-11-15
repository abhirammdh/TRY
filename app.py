import streamlit as st
import requests
import json
from downloader import download_video_or_playlist


# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="RAVANA YT DOWNLOADER",
    layout="centered"
)

# ---------------------------
# CUSTOM CSS (UI DESIGN)
# ---------------------------
st.markdown("""
<style>

body, .main {
    background: linear-gradient(135deg, #0d0d0d, #1a1a1a);
    color: white;
}

/* NAVBAR */
.navbar {
    background: rgba(255, 255, 255, 0.05);
    padding: 12px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 18px;
    font-size: 18px;
    font-weight: 700;
    color: #ff1f52;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
}

/* TITLES */
.big-title {
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    color: #ff1f52;
    margin-top: -10px;
}

.sub-text {
    text-align: center;
    font-size: 15px;
    color: #bbbbbb;
}

/* CARD */
.glass-card {
    background: rgba(255, 255, 255, 0.08);
    padding: 25px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    margin-top: 25px;
}

.stButton > button {
    width: 100%;
    background: #ff1f52;
    color: white;
    font-weight: 700;
    border-radius: 10px;
    padding: 10px;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #ff0037;
    transform: scale(1.02);
}

.format-box {
    background: rgba(255,255,255,0.08);
    padding: 10px;
    border-radius: 10px;
    margin-top: 5px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# NAV BAR
# ---------------------------
st.markdown("<div class='navbar'>RAVANA · VIDEO · AUDIO · PLAYLIST</div>", unsafe_allow_html=True)

# ---------------------------
# HEADER TITLE
# ---------------------------
st.markdown("<div class='big-title'>RAVANA YT DOWNLOADER</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Fast · Clean · Powerful</div>", unsafe_allow_html=True)

# ---------------------------
# MAIN CARD
# ---------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

url = st.text_input("YouTube URL")

show_info = False
video_info = {}

# ---------- Fetch Thumbnail + Details ----------
if url.strip():
    try:
        info_url = f"https://noembed.com/embed?url={url}"
        response = requests.get(info_url).json()

        if "title" in response:
            show_info = True
            video_info["title"] = response["title"]
            video_info["thumbnail"] = response.get("thumbnail_url", "")
    except:
        pass

if show_info:
    st.write("### 🎬 Video Preview")
    st.image(video_info["thumbnail"], width=350)
    st.write(f"**Title:** {video_info['title']}")

# ---------- OPTIONS ----------
col1, col2 = st.columns(2)
with col1:
    download_type = st.radio("Download Type", ["video", "audio"])

with col2:
    content_type = st.radio("Content Type", ["Video", "Playlist"])

quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
zip_output = st.checkbox("Zip Output (Playlist Only)")

# ---------- SHOW AVAILABLE FORMATS BUTTON ----------
if url.strip():
    if st.button("Show Available Qualities"):
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                meta = ydl.extract_info(url, download=False)
                formats = meta.get("formats", [])

                st.write("### 📌 Available Formats")
                for f in formats:
                    res = f.get("height")
                    ext = f.get("ext")
                    fps = f.get("fps")
                    if res:
                        st.markdown(
                            f"<div class='format-box'>Resolution: {res}p | Format: {ext} | FPS: {fps}</div>",
                            unsafe_allow_html=True
                        )
        except Exception as e:
            st.error(f"Could not fetch formats: {e}")

# ---------------------------
# DOWNLOAD BUTTON
# ---------------------------
submit = st.button("Start Download")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# PROCESS DOWNLOAD
# ---------------------------
if submit:
    if not url.strip():
        st.error("❌ Enter a valid YouTube URL")
    else:
        try:
            st.info("⏳ Downloading... please wait...")

            result = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=zip_output
            )

            st.success("✅ Download completed!")

            if zip_output:
                st.download_button(
                    "Download ZIP File",
                    result,
                    file_name="ravana_download.zip"
                )

            else:
                st.write("### Your Files:")
                for fp in result:
                    filename = fp.split("/")[-1]
                    with open(fp, "rb") as f:
                        st.download_button(
                            f"Download {filename}",
                            f,
                            file_name=filename
                        )

        except Exception as e:
            st.error(f"❌ Error: {e}")
