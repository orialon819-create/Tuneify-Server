import sqlite3

try:
    # 1. Connect to the database
    # Make sure the path "../tuneify.db" is correct relative to this script!
    conn = sqlite3.connect("../tuneify.db")
    cursor = conn.cursor()

    # 2. Execute the first command (Playlists)
    print("Adding cover_url to playlists...")
    cursor.execute("ALTER TABLE playlists ADD COLUMN cover_url TEXT DEFAULT 'default_playlist.png';")

    # 3. Execute the second command (Songs)
    print("Adding cover_url to songs...")
    cursor.execute("ALTER TABLE songs ADD COLUMN cover_url TEXT DEFAULT 'default_song.png';")

    # 4. Commit the changes and close
    conn.commit()
    print("Database updated successfully!")

except sqlite3.OperationalError as e:
    # This happens if the column already exists
    print(f"Notice: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals():
        conn.close()