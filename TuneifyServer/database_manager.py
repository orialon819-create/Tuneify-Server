import sqlite3
import hashlib
import json

# Handles all direct SQL queries to the database.
class DatabaseManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    # Checks if a username exists- if not, inserts a new user record into the users table
    def add_user(self, first_name, last_name, email, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.cursor.fetchone():
            return "ERROR|User already exists"

        self.cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, username, password))
        self.conn.commit()
        return "OK|User added successfully"

    # Fetches all data for a specific user based on their username
    def get_user(self, username):
        self.cursor.execute("SELECT id, first_name, last_name, email, username FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        if user:
            # Return as JSON string for Android to parse easily
            user_data = {"id": user[0], "first_name": user[1], "last_name": user[2], "email": user[3], "username": user[4]}
            return f"OK|{json.dumps(user_data)}"
        return "ERROR|User not found"

    # Validates login by retrieving the ID and password for a given username
    def verify_user(self, username, password):
        self.cursor.execute("SELECT id, first_name, last_name, email, username, password FROM users WHERE username=?",
                            (username,))
        row = self.cursor.fetchone()

        if row and row[5] == password:  # row[5] is the password column
            user_data = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "username": row[4]  # ADD THIS LINE
            }
            return f"OK|{json.dumps(user_data)}"
        return "ERROR|Invalid credentials"

    # Updates specific profile information (names or email) for an existing user
    def update_user_field(self, username, field, new_value):
        allowed_fields = ["first_name", "last_name", "email"]
        if field not in allowed_fields:
            return "ERROR|Invalid field"
        self.cursor.execute(f"UPDATE users SET {field} = ? WHERE username = ?", (new_value, username))
        self.conn.commit()
        return "OK|Update successful"

    # Fetches the entire song library as a JSON string for the Android UI
    def get_all_songs(self):
        self.cursor.execute("SELECT id, title, artist, file_name, stream_url, mood, mood_score, lyrics FROM songs")
        rows = self.cursor.fetchall()
        songs_list = []
        for r in rows:
            songs_list.append({
                "id": r[0], "title": r[1], "artist": r[2], "file_name": r[3],
                "stream_url": r[4], "mood": r[5], "mood_score": r[6], "lyrics": r[7]
            })
        return f"OK|{json.dumps(songs_list)}"

    def search_songs(self, query):
        like = f"%{query}%"
        self.cursor.execute("""
            SELECT id, title, artist FROM songs
            WHERE title LIKE ? OR artist LIKE ?
        """, (like, like))
        results = self.cursor.fetchall()
        if results:
            songs_list = [{"id": r[0], "title": r[1], "artist": r[2]} for r in results]
            return f"OK|{json.dumps(songs_list)}"
        return "ERROR|No songs found"

    def get_songs_by_mood(self, mood):
        self.cursor.execute("SELECT stream_url FROM songs WHERE mood=? LIMIT 1", (mood,))
        row = self.cursor.fetchone()
        return f"OK|{row[0]}" if row else "ERROR|No song found"

    # --- PLAYLIST METHODS ---

    def create_playlist(self, user_id, playlist_name):
        try:
            self.cursor.execute("INSERT INTO playlists (name, user_id) VALUES (?, ?)", (playlist_name, user_id))
            self.conn.commit()
            return f"OK|{self.cursor.lastrowid}"
        except Exception as e:
            return f"ERROR|{str(e)}"

    def get_user_playlists(self, user_id):
        # Added user_id to the SELECT
        self.cursor.execute("SELECT id, name, user_id FROM playlists WHERE user_id=?", (user_id,))
        rows = self.cursor.fetchall()

        # Matching the keys to what Kotlin expects: "id", "name", "user_id"
        playlists = [{"id": r[0], "name": r[1], "user_id": r[2]} for r in rows]

        return f"OK|{json.dumps(playlists)}"

    def update_playlist_name(self, playlist_id, new_name):
        self.cursor.execute("UPDATE playlists SET name=? WHERE id=?", (new_name, playlist_id))
        self.conn.commit()
        return "OK|Playlist updated"

    def delete_playlist(self, playlist_id):
        self.cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=?", (playlist_id,))
        self.cursor.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
        self.conn.commit()
        return "OK|Playlist deleted"

    def add_songs_to_playlist(self, playlist_id, song_ids):
        try:
            for s_id in song_ids:
                self.cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)", (playlist_id, s_id))
            self.conn.commit()
            return "OK|Songs added"
        except Exception as e:
            return f"ERROR|{str(e)}"

    def add_single_song_to_playlist(self, playlist_id, song_id):
        """Adds exactly one song to a playlist. Used by the Search Page popup."""
        try:
            self.cursor.execute(
                "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
                (playlist_id, song_id)
            )
            self.conn.commit()
            return "OK|Song added"
        except Exception as e:
            return f"ERROR|{str(e)}"

    def get_playlist_songs(self, playlist_id):
        self.cursor.execute("""
            SELECT songs.id, songs.title, songs.artist
            FROM songs
            JOIN playlist_songs ON songs.id = playlist_songs.song_id
            WHERE playlist_songs.playlist_id=?
        """, (playlist_id,))
        rows = self.cursor.fetchall()
        if rows:
            songs = [{"id": r[0], "title": r[1], "artist": r[2]} for r in rows]
            return f"OK|{json.dumps(songs)}"
        return "ERROR|No songs in playlist"

    def remove_song_from_playlist(self, playlist_id, song_id):
        self.cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=? AND song_id=?", (playlist_id, song_id))
        self.conn.commit()
        return "OK|Song removed from playlist"

    def close(self):
        self.conn.close()