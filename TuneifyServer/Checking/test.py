import sqlite3

# 1. Connect to the database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# 2. Define the User ID you're looking for
target_user_id = 1

# 3. Execute the query using a placeholder (?) for security
# This prevents "SQL Injection"
cursor.execute("SELECT * FROM playlists WHERE user_id = ?", (target_user_id,))

# 4. Fetch the results
playlists = cursor.fetchall()

# 5. Print the results to see if it worked
for p in playlists:
    print(f"Playlist ID: {p[0]}, Name: {p[1]}, Owner ID: {p[2]}")

# 6. Close the connection
conn.close()