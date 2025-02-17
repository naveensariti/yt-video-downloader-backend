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
    allow_origins=["*"],  # Adjust for production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the download directory in a temporary path
download_dir = "/tmp/downloads"
os.makedirs(download_dir, exist_ok=True)

# Mount static files (e.g., for index.html)
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")

@app.get("/")
async def root():
    # Ensure index.html exists in the "static" directory
    return FileResponse(os.path.join(os.getcwd(), "static", "index.html"))

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

    output_path = os.path.join(download_dir, "video.mp4")

    yt_dlp_opts = {
        "format": quality_formats[quality],
        "outtmpl": output_path,
        "cookies": os.path.join(os.getcwd(), "cookies.json"),  # Ensure cookies.json exists
    }

    try:
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([link])
        return {"status": "Download completed successfully."}
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Render uses the PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)
