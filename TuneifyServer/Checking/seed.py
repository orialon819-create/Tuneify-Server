import sqlite3

# --- SETTINGS ---
MY_IP = "192.168.1.30"       # <--- PUT YOUR IP HERE
FILE_NAME = "happy1.mp3"  # <--- PUT YOUR ACTUAL FILE NAME HERE
MOOD = "Happy"

# The Link that your Android app will use later
stream_url = f"http://{MY_IP}:8000/{FILE_NAME}"

conn = sqlite3.connect("tuneify.db")
cursor = conn.cursor()

# Insert the song into the new table structure
cursor.execute("""
    INSERT INTO songs (title, artist, file_name, stream_url, mood, mood_score, lyrics)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    FILE_NAME.replace('.mp3', ''), # Title (removes the .mp3)
    "Copyright Free Artist",       # Artist
    FILE_NAME,                     # file_name
    stream_url,                    # The URL for streaming
    MOOD,                          # Category
    0.9,                           # Mood Score (90% happy)
    "Instrumental"                 # Lyrics
))

conn.commit()
conn.close()

print(f"Success! {FILE_NAME} added to database.")
print(f"Streaming Link: {stream_url}")