import streamlit as st
import subprocess
import shlex
import threading
import time
import os
import shutil
import re
import queue
from pathlib import Path

# ----------------------- Helpers -----------------------

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return path

def build_yt_dlp_cmd(url: str, outtmpl: str, resolution: str, download_playlist: bool):
    """Build yt-dlp command for VIDEO + AUDIO (mp4 merged)."""
    cmd = [
        "yt-dlp",
        "--newline",
        "--no-warnings",
        "--no-color",
        "-c",
        "--ignore-errors",
        "--no-overwrites",
        "--yes-playlist" if download_playlist else "--no-playlist",
        "-o", outtmpl,
    ]

    # VIDEO + AUDIO merged
    if resolution == "auto":
        fmt = "bestvideo+bestaudio/best"
    else:
        fmt = f"bestvideo[height<={resolution}]+bestaudio/best"

    # Force output MP4 container
    cmd += ["-f", fmt, "--merge-output-format", "mp4"]

    cmd.append(url)
    return cmd


def run_subprocess(cmd, workdir: str, stop_event, proc_container):
    """Run yt-dlp and stream logs line-by-line."""
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        proc_container["proc"] = proc
    except FileNotFoundError:
        yield f"[ERROR] Command not found: {cmd[0]}. Please ensure it is installed and in PATH."
        return
    except Exception as e:
        yield f"[ERROR] Failed to start subprocess: {e}"
        return

    try:
        # Read line by line
        for line in iter(proc.stdout.readline, ""):
            line = line.strip()
            if stop_event.is_set():
                proc.kill()
                yield "[INFO] Download stopped by user."
                return
            if line:
                yield line
        
        proc.wait()
        yield f"[INFO] Finished with code {proc.returncode}"
    except Exception as e:
        try: proc.kill()
        except: pass
        yield f"[ERROR] {e}"


def parse_progress(line: str):
    """Extract percent using regex."""
    match = re.search(r'(\d+(?:\.\d+)?)%', line)
    if match:
        try:
            pct = float(match.group(1))
            return int(max(0, min(100, pct)))
        except:
            return None
    return None

# -------------------- Worker Thread --------------------

def worker(url, output_folder, resolution, playlist_flag, msg_queue, stop_event, proc_container):
    try:
        msg_queue.put(("LOG", f"[INFO] Thread started for {url}"))
        out_base = ensure_dir(Path(output_folder))
        
        # Smart output template
        if playlist_flag:
            # Playlist: Folder/PlaylistName/Title.ext
            outtmpl = "%(playlist_title)s/%(title)s.%(ext)s"
        else:
            # Single Video: Folder/Title.ext (No subfolder)
            outtmpl = "%(title)s.%(ext)s"

        cmd = build_yt_dlp_cmd(url, outtmpl, resolution, playlist_flag)

        msg_queue.put(("LOG", " ".join(shlex.quote(x) for x in cmd)))
        msg_queue.put(("LOG", "[INFO] Starting download..."))

        for line in run_subprocess(cmd, str(out_base), stop_event, proc_container):
            msg_queue.put(("LOG", line))
            pct = parse_progress(line)
            if pct is not None:
                msg_queue.put(("PROGRESS", pct))

        # Create ZIP if completed and not stopped
        if not stop_event.is_set():
            try:
                folders = [p for p in Path(output_folder).iterdir() if p.is_dir()]
                if display_path := next((p for p in folders if p.stat().st_mtime > time.time() - 3600), None) or (folders[0] if folders else None):
                     # Try to find recently modified folder, else pick first
                    pass
                
                # Simplified ZIP logic: just zip the download folder's content if it's a playlist, 
                # or finding the specific output is hard without parsing JSON. 
                # Let's zip the 'downloads' folder content for now or better, the subfolder created.
                # If 'yes-playlist' is used, it usually creates a folder if the template has %(playlist)s
                
                # Check for directories in output_folder
                subdirs = [x for x in Path(output_folder).iterdir() if x.is_dir()]
                if subdirs:
                     # Zip the most modified one?
                    target = max(subdirs, key=lambda x: x.stat().st_mtime)
                    zip_path = shutil.make_archive(str(target), "zip", root_dir=str(target))
                    msg_queue.put(("ZIP", zip_path))
                    msg_queue.put(("LOG", f"[INFO] ZIP created: {os.path.basename(zip_path)}"))
            except Exception as e:
                msg_queue.put(("LOG", f"[ERROR] ZIP creation failed: {e}"))
            
            # Send explicit success message
            msg_queue.put(("SUCCESS", "Video has been downloaded"))
                
    except Exception as e:
        msg_queue.put(("LOG", f"[CRITICAL ERROR] Worker failed: {e}"))
    finally:
        msg_queue.put(("DONE", None))

# --------------------- Streamlit UI ---------------------

st.set_page_config(page_title="YT Playlist Downloader", layout="wide")
st.title("🎬 YouTube Playlist Downloader (Video + Audio MP4)")

st.sidebar.header("Options")
url = st.sidebar.text_input("YouTube URL (Video or Playlist)", "")
download_playlist_flag = st.sidebar.checkbox("Download full playlist", True)
resolution = st.sidebar.selectbox("Max Resolution", ["auto", "1080", "720", "480", "360"], index=1)
output_folder = st.sidebar.text_input("Output Folder", value=str(Path.cwd() / "downloads"))

st.sidebar.caption("Requires yt-dlp + ffmpeg installed.")

if st.sidebar.button("🔄 Reset App State"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -------------------- Session state --------------------

if "initialized" not in st.session_state:
    st.session_state.log_lines = []
    st.session_state.progress = 0
    st.session_state.is_running = False
    st.session_state.zip_path = None
    st.session_state.zip_path = None
    st.session_state.msg_queue = queue.Queue()
    st.session_state.stop_event = threading.Event()
    st.session_state.proc_container = {}
    st.session_state.success_message = None
    st.session_state.initialized = True

# -------------------- UI Layout --------------------

col1, col2 = st.columns([2, 1])

with col1:
    start = st.button("▶ Start Download", disabled=st.session_state.is_running)
    stop = st.button("⛔ Stop", disabled=not st.session_state.is_running)
    
    st.subheader("Logs")
    if st.session_state.get("success_message"):
        st.success(st.session_state.success_message)

    log_area = st.empty()
    st.text_area("Logs", "\n".join(st.session_state.log_lines), height=400, key="logs_display", disabled=True)

with col2:
    st.subheader("Progress")
    progress_bar = st.progress(st.session_state.progress)

# -------------------- Logic & Polling --------------------

# Process messages from queue
while not st.session_state.msg_queue.empty():
    try:
        msg_type, payload = st.session_state.msg_queue.get_nowait()
        if msg_type == "LOG":
            st.session_state.log_lines.append(payload)
        elif msg_type == "PROGRESS":
            st.session_state.progress = payload
        elif msg_type == "ZIP":
            st.session_state.zip_path = payload
        elif msg_type == "SUCCESS":
            st.session_state.success_message = payload
        elif msg_type == "DONE":
            st.session_state.is_running = False
    except queue.Empty:
        break

# Button Actions
if start and not st.session_state.is_running:
    if not url.strip():
        st.error("Enter a URL first.")
    else:
        # Reset state
        st.session_state.log_lines = []
        st.session_state.progress = 0
        st.session_state.zip_path = None
        st.session_state.success_message = None # Reset success message
        st.session_state.is_running = True
        st.session_state.stop_event.clear()
        st.session_state.proc_container = {}
        
        # Clear queue
        with st.session_state.msg_queue.mutex:
            st.session_state.msg_queue.queue.clear()

        th = threading.Thread(
            target=worker,
            args=(
                url, 
                output_folder, 
                resolution, 
                download_playlist_flag, 
                st.session_state.msg_queue, 
                st.session_state.stop_event, 
                st.session_state.proc_container
            ),
            daemon=True,
        )
        th.start()
        st.rerun()

if stop and st.session_state.is_running:
    st.session_state.stop_event.set()
    proc = st.session_state.proc_container.get("proc")
    if proc:
        try:
            proc.kill() 
            st.session_state.log_lines.append("[INFO] Kill signal sent.")
        except:
            pass

# Auto-refresh if running
if st.session_state.is_running:
    time.sleep(1)
    st.rerun()

# Download ZIP button
if st.session_state.zip_path:
    with open(st.session_state.zip_path, "rb") as f:
        st.download_button(
            "📦 Download ZIP",
            f.read(),
            file_name=os.path.basename(st.session_state.zip_path),
            mime="application/zip",
        )
