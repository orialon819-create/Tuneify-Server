import sqlite3

# Connect to your database
conn = sqlite3.Connection("../tuneify.db")
cursor = conn.cursor()

# 1. To delete by ID (Best way)
song_id = 4
cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))

# 2. OR to delete by Mood (Careful: this deletes ALL songs with that mood)
# cursor.execute("DELETE FROM songs WHERE mood = 'Energetic'")

conn.commit()
print("Row deleted successfully.")
conn.close()