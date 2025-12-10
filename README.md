# YouTube Playlist Downloader (Streamlit + yt-dlp)

A simple, robust Streamlit application to download YouTube videos and playlists in high quality (Video + Audio merged).

![App Screenshot](https://raw.githubusercontent.com/placeholder-image.png)

## Features

- **Video + Audio Merging**: Automatically selects the best video (up to 1080p) and best audio, merging them into a single MP4 file.
- **Playlist Support**: Download entire playlists into organized subfolders.
- **Smart Queue**: Thread-safe background downloads so the UI remains responsive.
- **Stop Support**: Ability to cleanly stop active downloads.
- **ZIP Export**: Automatically zips downloaded playlists for easy transfer.

## Requirements

1.  **Python 3.8+**
2.  **FFmpeg**: Must be installed and accessible in your system PATH.
    *   *Mac*: `brew install ffmpeg`
    *   *Windows*: Download and add to PATH.
    *   *Linux*: `sudo apt install ffmpeg`

## Installation

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd yt_playlist_streamlit
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

2.  Open the URL provided in the terminal (usually `http://localhost:8501`).

3.  Enter a YouTube URL, select resolution, and click **Start Download**.

## Troubleshooting

- **Nothing happening?**: Click **Reset App State** in the sidebar.
- **FFmpeg error?**: Ensure `ffmpeg` is installed (`ffmpeg -version`).

## License

MIT
