import sqlite3

# Connect to your database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# You must use cursor.execute() for each SQL command
cursor.execute("INSERT INTO playlists (name, user_id, cover_url) VALUES ('Top Pop Hits', 0, 'cover_toppophits.png')")

cursor.execute("INSERT INTO playlists (name, user_id, cover_url) VALUES ('80s Mix', 0, 'cover_80smix.png')")

cursor.execute("INSERT INTO playlists (name, user_id, cover_url) VALUES ('Throwback Mix', 0, 'cover_tbmix.png')")

conn.commit()

print("Successfully updated playlists.")
conn.close()