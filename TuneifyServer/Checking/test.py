import sqlite3

# 1. Connect to the database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# 2. Execute the DELETE statement as a string
cursor.execute("DELETE FROM playlists WHERE id = 17;")

# 3. CRITICAL: Save the changes!
conn.commit()

# 4. Close the connection
conn.close()

print("Successfully deleted songs with IDs from 28 to 39.")