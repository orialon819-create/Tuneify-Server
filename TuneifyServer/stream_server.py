from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import uvicorn
from urllib.parse import unquote

app = FastAPI()
MUSIC_DIRECTORY = "./music_library"


@app.get("/stream/{song_title}")
async def stream_music(song_title: str):
    # This converts "Blinding%20Lights" back to "Blinding Lights"
    decoded_title = unquote(song_title)
    file_path = os.path.join(MUSIC_DIRECTORY, f"{decoded_title}.mp3")

    print(f"Client requested: {decoded_title}")  # For debugging

    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/mpeg")

    print(f"Error: {file_path} not found!")
    raise HTTPException(status_code=404, detail="Song file not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)