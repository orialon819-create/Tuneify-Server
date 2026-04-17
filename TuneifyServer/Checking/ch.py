import sqlite3

# Connect to your database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# Update cover_url based on title
cursor.execute(
    "UPDATE songs SET cover_url = ? WHERE title = ?",
    ("olivia.png", "sad1")
)

conn.commit()

print("Successfully updated.")
conn.close()