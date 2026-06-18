import sqlite3

conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# Format: (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
songs = [
    ("Party Rock Anthem", "LMFAO", "Party Rock Anthem.mp3", "/TuneifyServer/music_library/Party Rock Anthem.mp3", "Energetic", 0.7, "", "pra_icon.jpg"),
    ("Let Her Go", "Artist", "Let Her Go.mp3", "/TuneifyServer/music_library/Let Her Go.mp3", "Calm", 0.7, "", "lethergo_icon.png"),
    ("song3", "Artist", "song3.mp3", "/TuneifyServer/music_library/song3.mp3", "Angry", 0.7, "", "checker_icon.png"),
    ("song4", "Artist", "song4.mp3", "/TuneifyServer/music_library/song4.mp3", "Happy", 0.7, "", "checker_icon.png"),
    ("song5", "Artist", "song5.mp3", "/TuneifyServer/music_library/song5.mp3", "Happy", 0.7, "", "checker_icon.png")
]

cursor.executemany("""
    INSERT INTO songs (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", songs)

conn.commit()

print(f"Successfully added {len(songs)} songs to the database!")

conn.close()