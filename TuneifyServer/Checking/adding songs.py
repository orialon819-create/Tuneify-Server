import sqlite3

conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# Format: (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
songs = [
    ("9 To 5", "Dolly Parton", "9 To 5.mp3", "/TuneifyServer/music_library/9 To 5.mp3", None, 0, "Instrumental", "cover_9to5.png"),
    ("24K Magic", "Bruno Mars", "24K Magic.mp3", "/TuneifyServer/music_library/24K Magic.mp3", None, 0, "Instrumental", "cover_24magic.png"),
    ("Africa", "Toto", "Africa.mp3", "/TuneifyServer/music_library/Africa.mp3", None, 0, "Instrumental", "cover_africa.png"),
    ("All Star", "Smash Mouth", "All Star.mp3", "/TuneifyServer/music_library/All Star.mp3", None, 0, "Instrumental", "cover_allstar.png"),
    ("Beauty And A Beat", "Justin Bieber", "Beauty And A Beat.mp3", "/TuneifyServer/music_library/Beauty And A Beat.mp3", None, 0, "Instrumental", "cover_beautyandabeat.png"),
    ("Complicated", "Avril Lavigne", "Complicated.mp3", "/TuneifyServer/music_library/Complicated.mp3", None, 0, "Instrumental", "cover_complicated.png"),
    ("Don't Dream It's Over", "Crowded House", "Don't Dream It's Over.mp3", "/TuneifyServer/music_library/Don't Dream It's Over.mp3", None, 0, "Instrumental", "cover_dontdreamitsover.png"),
    ("Good 4 U", "Olivia Rodrigo", "Good 4 U.mp3", "/TuneifyServer/music_library/Good 4 U.mp3", None, 0, "Instrumental", "cover_sour.png"),
    ("Hey There Delilah", "Plain White T's", "Hey There Delilah.mp3", "/TuneifyServer/music_library/Hey There Delilah.mp3", None, 0, "Instrumental", "cover_heytheredelilah.png"),
    ("Ironic", "Alanis Morissette", "Ironic.mp3", "/TuneifyServer/music_library/Ironic.mp3", None, 0, "Instrumental", "cover_ironic.png"),
    ("Just Dance", "Lady Gaga", "Just Dance.mp3", "/TuneifyServer/music_library/Just Dance.mp3", None, 0, "Instrumental", "cover_justdance.png"),
    ("Still Into You", "Paramore", "Still Into You.mp3", "/TuneifyServer/music_library/Still Into You.mp3", None, 0, "Instrumental", "cover_stillintoyou.png"),
    ("Take On Me", "A-ha", "Take On Me.mp3", "/TuneifyServer/music_library/Take On Me.mp3", None, 0, "Instrumental", "cover_takeonme.png"),
    ("Under Pressure", "Queen & David Bowie", "Under Pressure.mp3", "/TuneifyServer/music_library/Under Pressure.mp3", None, 0, "Instrumental", "cover_underpressure.png")
]

cursor.executemany("""
    INSERT INTO songs (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", songs)

conn.commit()

print(f"Successfully added {len(songs)} songs to the database!")

conn.close()