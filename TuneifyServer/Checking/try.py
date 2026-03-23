import sqlite3

# Connect to DB
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# ---- SONG INFO ----
FILE_NAME = "energetic1.mp3"
MOOD = "Energetic"

# This is the IMPORTANT part:
# Path relative to the HTTP server root
STREAM_PATH = "/TuneifyServer/music_library/" + FILE_NAME

cursor.execute("""
    INSERT INTO songs (title, artist, file_name, stream_url, mood, mood_score, lyrics)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    FILE_NAME.replace(".mp3", ""),
    "Copyright Free",
    FILE_NAME,
    STREAM_PATH,
    MOOD,
    0.9,
    "Instrumental"
))

conn.commit()
conn.close()

print("Song inserted correctly (IP-independent) 🎵")
