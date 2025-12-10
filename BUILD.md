# Build and Run Guide

This guide provides detailed instructions on how to set up the environment and run the YouTube Playlist Downloader locally.

## Prerequisite: FFmpeg
This application strictly requires **FFmpeg** to merge video and audio streams.

### macOS
```bash
brew install ffmpeg
```

### Windows
1.  Download the build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2.  Extract the ZIP file.
3.  Add the `bin` folder (containing `ffmpeg.exe`) to your System PATH variables.
4.  Verify by running `ffmpeg -version` in Command Prompt.

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

---

## Method 1: Python Virtual Environment (Recommended)

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <your-repo-url>
    cd yt_playlist_streamlit
    ```

2.  **Create a Virtual Environment**:
    ```bash
    # macOS/Linux
    python3 -m venv venv
    
    # Windows
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    ```bash
    # macOS/Linux
    source venv/bin/activate
    
    # Windows
    venv\Scripts\activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

---

## Method 2: Docker (Optional)

If you have Docker installed, you can build an image to isolate the environment.

1.  **Create a `Dockerfile`** (if not present):
    ```dockerfile
    FROM python:3.9-slim
    
    # Install ffmpeg
    RUN apt-get update && apt-get install -y ffmpeg
    
    WORKDIR /app
    
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . .
    
    EXPOSE 8501
    
    CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
    ```

2.  **Build the Image**:
    ```bash
    docker build -t yt-downloader .
    ```

3.  **Run the Container**:
    ```bash
    docker run -p 8501:8501 -v $(pwd)/downloads:/app/downloads yt-downloader
    ```
    *Note: The `-v` flag mounts your local `downloads` folder so downloaded files persist on your machine.*
