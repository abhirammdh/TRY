# app.py — Final (uses downloader.download_video_or_playlist)
import streamlit as st
import os
import json
import time
from threading import Thread
from downloader import download_video_or_playlist

# ---------------- config ----------------
st.set_page_config(page_title="Ravana Downloader", layout="wide")
DOWNLOAD_DIR = "downloads"
HISTORY_FILE = os.path.join(DOWNLOAD_DIR, "history.json")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- session / history ----------------
if "history" not in st.session_state:
    st.session_state.history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as hf:
                st.session_state.history = json.load(hf)
        except Exception:
            st.session_state.history = []

def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as hf:
            json.dump(st.session_state.history, hf, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_history_entry(title, mode, quality, files):
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "title": title,
        "mode": mode,
        "quality": quality,
        "files": files
    }
    st.session_state.history.insert(0, entry)
    # keep only recent 300
    st.session_state.history = st.session_state.history[:300]
    save_history()

# ---------------- theme ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# minimal CSS for dark/light
if st.session_state.theme == "dark":
    BG = "#0b0d0f"
    TEXT = "#e6fff0"
else:
    BG = "#ffffff"
    TEXT = "#111111"

st.markdown(
    f"""
    <style>
      body {{ background: {BG}; color: {TEXT}; }}
      .stButton>button{{ border-radius:8px; padding:8px 12px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- navigation ----------------
st.sidebar.title("RAVANA")
if st.sidebar.button("Toggle theme"):
    toggle_theme()

page = st.sidebar.radio("Menu", ["Home", "Download", "History", "About"])

# ---------------- Home ----------------
if page == "Home":
    st.title("🔥 Ravana YT Downloader")
    st.write("Fast, reliable downloader using your `downloader.py`.")
    st.write("- No cookies required")
    st.write("- Video/audio/playlist support")
    st.write("- Progress bar & history")
    st.stop()

# ---------------- Download ----------------
if page == "Download":
    st.title("📥 Download")

    url = st.text_input("YouTube URL (video or playlist)")
    mode = st.radio("Mode", ["video", "audio"], index=0, horizontal=True)

    # quality only relevant for video; downloader will accept strings like "720p"
    if mode == "video":
        quality = st.selectbox("Select quality", ["240p","360p","480p","720p","1080p","1440p (2K)","2160p (4K)"], index=3)
    else:
        quality = "audio"

    # run downloader in background thread and poll for progress
    if st.button("Start Download"):
        if not url or not url.strip():
            st.error("Please enter a valid YouTube URL.")
        else:
            # shared container for thread results
            shared = {"files": None, "error": None}

            def target():
                try:
                    res = download_video_or_playlist(url, quality=quality if mode=="video" else "720p", mode=mode)
                    shared["files"] = res
                except Exception as e:
                    shared["error"] = str(e)

            thread = Thread(target=target, daemon=True)
            thread.start()

            pbar = st.progress(0)
            status = st.empty()

            # Poll while thread is alive — show staged progress to indicate activity
            stages = [10, 30, 50, 70, 90]
            i = 0
            while thread.is_alive():
                p = stages[i % len(stages)]
                pbar.progress(p)
                status.info(f"Working... {p}%")
                time.sleep(0.6)
                i += 1

            # thread finished
            if shared.get("error"):
                status.error(f"Download failed: {shared['error']}")
                pbar.progress(0)
            else:
                files = shared.get("files") or []
                # files may contain None entries — filter them out safely
                good_files = []
                for f in files:
                    if not f:
                        continue
                    # if relative path returned, normalize
                    if isinstance(f, str) and os.path.exists(f):
                        good_files.append(f)
                    else:
                        # maybe downloader returned a filename without folder; try in downloads/
                        candidate = os.path.join(DOWNLOAD_DIR, os.path.basename(f)) if isinstance(f, str) else None
                        if candidate and os.path.exists(candidate):
                            good_files.append(candidate)
                        else:
                            # skip missing
                            continue

                if not good_files:
                    status.error("Download finished but no valid files were produced (all returned None or missing).")
                    pbar.progress(0)
                else:
                    pbar.progress(100)
                    status.success("Download complete.")
                    # show download buttons & save history
                    for fpath in good_files:
                        try:
                            with open(fpath, "rb") as fh:
                                st.download_button(label=f"Save {os.path.basename(fpath)}", data=fh.read(), file_name=os.path.basename(fpath))
                        except Exception as e:
                            st.warning(f"Could not open {fpath}: {e}")

                    add_title = os.path.basename(good_files[0])
                    add_history_entry(add_title, mode.capitalize(), quality, good_files)

    st.stop()

# ---------------- History ----------------
if page == "History":
    st.title("📜 Download History")
    if not st.session_state.history:
        st.info("No downloads yet.")
    else:
        for entry in st.session_state.history:
            st.write(f"**{entry['title']}** — {entry['mode']} {entry['quality']}")
            for p in entry.get("files", []):
                st.write(f"- {p}")
            st.markdown("---")
    if st.button("Clear history"):
        st.session_state.history = []
        save_history()
        st.success("History cleared.")
    st.stop()

# ---------------- About ----------------
if page == "About":
    st.title("About")
    st.write("Created by D. Abhiram")
    st.write("Uses your local `downloader.py` for downloads. No cookies required.")
    st.stop()
