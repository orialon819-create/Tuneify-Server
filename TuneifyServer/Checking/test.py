import sqlite3

# 1. Connect to the database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

song_ids = [12, 14, 17, 18, 20]
playlist_id = 12

for song_id in song_ids:
    cursor.execute("""
        INSERT INTO playlist_songs (playlist_id, song_id)
        VALUES (?, ?)
    """, (playlist_id, song_id))

# CRITICAL: Save the changes!
conn.commit()

# 6. Close the connection
conn.close()

print(f"Added songs {song_ids} to playlist {playlist_id} successfully.")