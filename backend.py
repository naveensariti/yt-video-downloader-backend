from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import yt_dlp

app = FastAPI()

# Allow all origins for CORS during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

download_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_dir, exist_ok=True)

# Mount static files (for index.html)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return FileResponse("index.html")  # Ensure index.html is served correctly

@app.post("/download")
async def download_video(link: str = Form(...), quality: str = Form(...)):
    """
    Download a YouTube video with the selected quality.
    """
    if not link or not quality:
        raise HTTPException(status_code=400, detail="Missing required fields.")

    # Mapping quality to yt-dlp format selection
    quality_formats = {
        "low": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "medium": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "high": "bestvideo[height<=1080]+bestaudio/best",
    }

    if quality not in quality_formats:
        raise HTTPException(
            status_code=400, detail="Invalid quality. Use 'low', 'medium', or 'high'."
        )

    output_path = os.path.join(download_dir, "video")
    yt_dlp_opts = {
        "format": quality_formats[quality],
        "outtmpl": output_path,
    }

    try:
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([link])
        return {"status": "Download completed successfully."}
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
