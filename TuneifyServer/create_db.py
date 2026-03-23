import sqlite3

# Connect to the database
conn = sqlite3.connect("tuneify.db")
cursor = conn.cursor()

# --- STEP 1: CLEANUP ---
# We drop tables to make sure the new columns (id, stream_url) are created

#cursor.execute("DROP TABLE IF EXISTS playlist_songs")


# --- STEP 2: CREATE TABLES ---

# Users Table (No changes made to your original columns)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    username TEXT,
    password TEXT
)
""")

# Songs Table (NEW: Added 'id' and 'stream_url', REMOVED 'lyrics')
cursor.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    file_name TEXT,
    stream_url TEXT,    
    mood TEXT,
    mood_score REAL,
    lyrics TEXT         
)
""")

# Playlists Table (No changes)
cursor.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Playlist-Songs Link (Now it links correctly to the Song ID!)
cursor.execute("""
CREATE TABLE IF NOT EXISTS playlist_songs (
    playlist_id INTEGER,
    song_id INTEGER,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
)
""")

conn.commit()
conn.close()
print("Database 'tuneify.db' has been refreshed and updated!")