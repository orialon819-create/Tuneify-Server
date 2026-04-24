import sqlite3

conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()





songs = [
    ("Drop Dead", "Olivia Rodrigo", "Drop Dead.mp3", "/TuneifyServer/music_library/Drop Dead.mp3", "happy", 0.7, "Instrumental", "cover_yspsfagsil.png"),
    ("Lacy", "Olivia Rodrigo", "Lacy.mp3", "/TuneifyServer/music_library/Lacy.mp3", "sad", 0.7, "Instrumental", "cover_guts.png"),
    ("Favorite Crime", "Olivia Rodrigo", "Favorite Crime.mp3", "/TuneifyServer/music_library/Favorite Crime.mp3", "calm", 0.7, "Instrumental", "cover_sour.png")
]

cursor.executemany("""
    INSERT INTO songs (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", songs)

# THIS IS THE MISSING PART:
conn.commit()

print(f"Successfully added {len(songs)} songs to the database!")

conn.close()
