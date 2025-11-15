import streamlit as st
from downloader import download_video_or_playlist

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="RAVANA YT DOWNLOADER",
    page_icon=None,
    layout="centered"
)

# ---------------------------
# CUSTOM STYLES
# ---------------------------
st.markdown("""
<style>

body, .main {
    background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
    color: white;
}

.big-title {
    font-size: 40px;
    font-weight: 800;
    text-align: center;
    color: #ff265a;
    margin-top: -20px;
    margin-bottom: 10px;
}

.sub-text {
    text-align: center;
    font-size: 15px;
    color: #bbbbbb;
    margin-top: -10px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.08);
    padding: 25px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    margin-top: 25px;
}

.stButton > button {
    width: 100%;
    background: #ff265a;
    color: white;
    font-weight: 700;
    border-radius: 10px;
    padding: 10px;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #ff003c;
    transform: scale(1.02);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# UI HEADER
# ---------------------------
st.markdown("<div class='big-title'>RAVANA YT DOWNLOADER</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Download YouTube Videos · Playlists · Audio · ZIP</div>", unsafe_allow_html=True)

# ---------------------------
# MAIN CARD
# ---------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

# INPUTS
url = st.text_input("YouTube URL")

col1, col2 = st.columns(2)
with col1:
    download_type = st.radio("Download Type", ["video", "audio"])
with col2:
    content_type = st.radio("Content Type", ["Video", "Playlist"])

quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
zip_output = st.checkbox("ZIP Output (For Playlist)")

submit = st.button("Start Download")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# PROCESS DOWNLOADING
# ---------------------------
if submit:
    if not url.strip():
        st.error("❌ Please enter a valid YouTube URL.")
    else:
        try:
            st.info("⏳ Downloading... Please wait...")
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
                for file_path in result:
                    filename = file_path.split("/")[-1]
                    with open(file_path, "rb") as f:
                        st.download_button(
                            f"Download {filename}",
                            f,
                            file_name=filename
                        )

        except Exception as e:
            st.error(f"❌ Error: {e}")
