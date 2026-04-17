from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uvicorn
from urllib.parse import unquote

app = FastAPI()

# --- 1. CONFIGURATION: FOLDER PATHS ---
# These are the actual folders on your computer's hard drive
MUSIC_DIRECTORY = "./music_library"
PLAYLIST_COVERS_DIR = "./playlist_covers"
SONG_COVERS_DIR = "./song_covers"

# This part automatically creates the folders if they don't exist yet
os.makedirs(MUSIC_DIRECTORY, exist_ok=True)
os.makedirs(PLAYLIST_COVERS_DIR, exist_ok=True)
os.makedirs(SONG_COVERS_DIR, exist_ok=True)

# --- 2. STATIC MOUNTING: THE "PUBLIC" WINDOWS ---
# Mounting tells FastAPI to treat a folder like a website directory.
# Without these lines, Android could NEVER "see" the images even if they exist.

# If Android asks for http://IP:8000/covers/playlist/image.jpg -> looks in ./playlist_covers
app.mount("/covers/playlist", StaticFiles(directory=PLAYLIST_COVERS_DIR), name="playlist_covers")

# If Android asks for http://IP:8000/covers/song/image.jpg -> looks in ./song_covers
app.mount("/covers/song", StaticFiles(directory=SONG_COVERS_DIR), name="song_covers")


# --- 3. MUSIC STREAMING ROUTE ---
@app.get("/stream/{song_name}")
async def stream_music(song_name: str):
    decoded_name = unquote(song_name)
    clean_name = decoded_name.replace("\\", "").replace("/", "")

    if not clean_name.lower().endswith(".mp3"):
        clean_name += ".mp3"

    file_path = os.path.join(MUSIC_DIRECTORY, clean_name)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")

    raise HTTPException(status_code=404, detail=f"File {clean_name} not found")


# --- 4. PLAYLIST COVER UPLOAD ROUTE ---
# This is how the file travels from the Phone's Gallery to your PC folder.
@app.post("/upload_playlist_cover/{playlist_id}")
async def upload_playlist_cover(playlist_id: int, file: UploadFile = File(...)):
    try:
        # Get the extension (jpg/png) so we don't lose the format
        extension = file.filename.split(".")[-1]

        # We rename it "cover_5.jpg" so it's easy to find later
        filename = f"cover_{playlist_id}.{extension}"
        file_path = os.path.join(PLAYLIST_COVERS_DIR, filename)

        # 'wb' means Write Binary - we are writing the image data to the disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # We return the filename so Android can later tell the Socket Server
        # to save this specific name in the SQL database.
        return {"status": "OK", "filename": filename}

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


if __name__ == "__main__":
    # Change '0.0.0.0' to your actual Local IP if needed for Android testing
    uvicorn.run(app, host="0.0.0.0", port=8000)