# Deploying to Streamlit Community Cloud

Since this app requires `ffmpeg`, special configuration is needed for deployment.

## 1. Prepare your GitHub Repository
Ensure your repository contains the following files:
*   `app.py`
*   `requirements.txt` (must include `streamlit` and `yt-dlp`)
*   `packages.txt` (Must contain `ffmpeg`. This tells Streamlit Cloud to install it.)

## 2. Push to GitHub
If you haven't already:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

## 3. Deploy
1.  Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2.  Click **New app**.
3.  Select your GitHub repository (`yt_playlist_streamlit`).
4.  Select `main` branch and `app.py` as the main file.
5.  Click **Deploy**.

Streamlit Cloud will automatically detect `packages.txt` and install FFmpeg before starting your app.
