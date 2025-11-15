import streamlit as st
import os
import json
import time
from downloader import download_video_or_playlist

# -----------------------------------------------------------
# CONFIG
# -----------------------------------------------------------
st.set_page_config(
    page_title="Ravana Downloader",
    layout="centered",
    page_icon="🔥"
)


# -----------------------------------------------------------
# THEME TOGGLE (Light / Dark)
# -----------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

theme_button = "🌙 Dark Mode" if st.session_state.theme == "light" else "☀️ Light Mode"
st.button(theme_button, on_click=toggle_theme)

# Custom CSS (no glow, smooth animations)
st.markdown(
    f"""
    <style>
        body {{
            background-color: {"#0d0d0d" if st.session_state.theme=="dark" else "#ffffff"};
            color: {"white" if st.session_state.theme=="dark" else "black"};    
        }}

        .download-btn {{
            padding: 10px 20px;
            border-radius: 12px;
            background: #ff4d4d;
            color: white;
            border: none;
            font-size: 18px;
            transition: 0.2s ease-in-out;
        }}

        .download-btn:hover {{
            transform: scale(1.05);
            background: #e60000;
        }}

        .nav {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .nav button {{
            padding: 10px 18px;
            border-radius: 10px;
            margin: 0 10px;
            background: #333;
            color: white;
            border: none;
            transition: 0.2s;
        }}

        .nav button:hover {{
            background: #555;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------
# Navigation (Home / Downloader / Credits)
# -----------------------------------------------------------
pages = ["Home", "Downloader", "Credits"]
choice = st.radio("Navigation", pages, horizontal=True)


# -----------------------------------------------------------
# HOME PAGE
# -----------------------------------------------------------
if choice == "Home":
    st.title("🔥 Ravana YouTube Downloader")
    st.subheader("Fast • Clean • Secure")

    st.markdown("""
    🚀 **Features:**
    - ✨ Video Downloader  
    - 🎵 Audio Downloader  
    - 🎞 Playlist Download  
    - 📥 Progress Bar  
    - 🕒 Download History  
    - 🌗 Dark Mode  
    - ⚡ Smooth UI Animations  
    - 🧩 No watermark  
    """)

    st.image(
        "https://i.ibb.co/6rJ6fCy/yt-banner.jpg",
        caption="Ravana Downloader",
        use_container_width=True
    )

    st.info("Go to the **Downloader** tab to start downloading 🔥")


# -----------------------------------------------------------
# DOWNLOADER PAGE
# -----------------------------------------------------------
elif choice == "Downloader":
    st.title("📥 Ravana Video/Audio Downloader")

    url = st.text_input("Enter YouTube Video or Playlist URL")

    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox("Download Type", ["video", "audio"])
    with col2:
        quality = st.selectbox("Video Quality", ["360p", "480p", "720p", "1080p"])

    # PROGRESS BAR
    progress = st.progress(0)
    status_text = st.empty()

    if st.button("Download Now", key="download", help="No watermark, fast download"):
        if not url.strip():
            st.error("❌ Please enter a valid URL")
        else:

            # Animate load
            status_text.write("⏳ Initializing download...")
            for i in range(20):
                progress.progress(i * 5)
                time.sleep(0.02)

            try:
                status_text.write("🚀 Downloading... Please wait...")
                files = download_video_or_playlist(url, quality, mode)

                progress.progress(100)
                st.success("🎉 Download Completed!")

                # Save download history
                if not os.path.exists("history.json"):
                    open("history.json", "w").write("[]")

                history = json.load(open("history.json"))
                history.append({"url": url, "files": files})
                json.dump(history, open("history.json", "w"), indent=4)

                # Show download buttons
                st.subheader("⬇ Your Downloads")
                for file in files:
                    if os.path.exists(file):
                        st.download_button(
                            label=f"Download {os.path.basename(file)}",
                            data=open(file, "rb"),
                            file_name=os.path.basename(file)
                        )

            except Exception as e:
                st.error(f"❌ Error: {e}")


    # VIEW DOWNLOAD HISTORY
    st.subheader("📜 Download History")
    if os.path.exists("history.json"):
        history = json.load(open("history.json"))
        for item in history[-5:][::-1]:
            st.write(f"🔗 {item['url']}")


# -----------------------------------------------------------
# CREDITS PAGE
# -----------------------------------------------------------
elif choice == "Credits":
    st.title("👨‍💻 Credits")

    st.markdown("""
    **Ravana YouTube Downloader**  
    Built by **Devulapalli Abhiram** ❤️

    - 🚀 Fastest YT Downloader  
    - 🧠 Streamlit + Python + yt-dlp  
    - 🎨 Custom UI Design  
    """)

    st.success("Made with ❤️ & Python")





