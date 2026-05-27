import sqlite3

conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT;")

conn.commit()
conn.close()

print("Migration complete")