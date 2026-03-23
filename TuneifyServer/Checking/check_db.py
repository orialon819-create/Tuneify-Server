import sqlite3

conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

print("Users:", cursor.execute("SELECT * FROM users").fetchall())
print("Songs:", cursor.execute("SELECT * FROM songs").fetchall())
print("Playlists:", cursor.execute("SELECT * FROM playlists").fetchall())
print("Playlist Songs:", cursor.execute("SELECT * FROM playlist_songs").fetchall())

conn.close()
