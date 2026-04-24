import sqlite3
import hashlib
import json

# Handles all direct SQL queries to the database.
class DatabaseManager:
    def __init__(self, db_file):
        # We use check_same_thread=False to allow multiple ClientHandlers to access the connection
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

    # Checks if a username exists- if not, inserts a new user record into the users table
    def add_user(self, first_name, last_name, email, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return "ERROR|User already exists"

            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, username, password)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, username, password))
            self.conn.commit()
            return "OK|User added successfully"
        finally:
            cursor.close()

    # Fetches all data for a specific user based on their username
    def get_user(self, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, first_name, last_name, email, username FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user:
                # Return as JSON string for Android to parse easily
                user_data = {"id": user[0], "first_name": user[1], "last_name": user[2], "email": user[3], "username": user[4]}
                return f"OK|{json.dumps(user_data)}"
            return "ERROR|User not found"
        finally:
            cursor.close()

    # Validates login by retrieving the ID and password for a given username
    def verify_user(self, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, first_name, last_name, email, username, password FROM users WHERE username=?",
                                (username,))
            row = cursor.fetchone()

            if row and row[5] == password:  # row[5] is the password column
                user_data = {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "username": row[4]
                }
                return f"OK|{json.dumps(user_data)}"
            return "ERROR|Invalid credentials"
        finally:
            cursor.close()

    # Updates specific profile information (names or email) for an existing user
    def update_user_field(self, username, field, new_value):
        cursor = self.conn.cursor()
        try:
            allowed_fields = ["first_name", "last_name", "email"]
            if field not in allowed_fields:
                return "ERROR|Invalid field"
            cursor.execute(f"UPDATE users SET {field} = ? WHERE username = ?", (new_value, username))
            self.conn.commit()
            return "OK|Update successful"
        finally:
            cursor.close()

    # Fetches the entire song library as a JSON string for the Android UI
    def get_all_songs(self):
        cursor = self.conn.cursor()
        try:
            # Added cover_url to the end of the SELECT
            cursor.execute("SELECT id, title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url FROM songs")
            rows = cursor.fetchall()
            songs_list = []
            for r in rows:
                songs_list.append({
                    "id": r[0], "title": r[1], "artist": r[2], "file_name": r[3],
                    "stream_url": r[4], "mood": r[5], "mood_score": r[6], "lyrics": r[7],
                    "cover_url": r[8]
                })
            return f"OK|{json.dumps(songs_list)}"
        finally:
            cursor.close()

    def search_songs(self, query):
        cursor = self.conn.cursor()
        try:
            like = f"%{query}%"
            # Added 'cover_url' to the SELECT statement
            cursor.execute("""
                SELECT id, title, artist, cover_url FROM songs
                WHERE title LIKE ? OR artist LIKE ?
            """, (like, like))
            results = cursor.fetchall()

            if results:
                # Added r[3] to the dictionary
                songs_list = [
                    {
                        "id": r[0],
                        "title": r[1],
                        "artist": r[2],
                        "cover_url": r[3]
                    } for r in results
                ]
                return f"OK|{json.dumps(songs_list)}"
            return "ERROR|No songs found"
        finally:
            cursor.close()

    def get_songs_by_mood(self, mood):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT stream_url FROM songs WHERE mood=? LIMIT 1", (mood,))
            row = cursor.fetchone()
            return f"OK|{row[0]}" if row else "ERROR|No song found"
        finally:
            cursor.close()

    # --- PLAYLIST METHODS ---

    def create_playlist(self, user_id, playlist_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO playlists (name, user_id) VALUES (?, ?)", (playlist_name, user_id))
            self.conn.commit()
            return f"OK|{cursor.lastrowid}"
        except Exception as e:
            return f"ERROR|{str(e)}"
        finally:
            cursor.close()

    def get_user_playlists(self, user_id):
        cursor = self.conn.cursor()
        try:
            # Added cover_url to the SELECT
            cursor.execute("SELECT id, name, user_id, cover_url FROM playlists WHERE user_id=?", (user_id,))
            rows = cursor.fetchall()

            # Added "cover_url": r[3] to the dictionary
            playlists = [{"id": r[0], "name": r[1], "user_id": r[2], "cover_url": r[3]} for r in rows]

            return f"OK|{json.dumps(playlists)}"
        finally:
            cursor.close()

    def update_playlist_name(self, playlist_id, new_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE playlists SET name=? WHERE id=?", (new_name, playlist_id))
            self.conn.commit()
            return "OK|Playlist updated"
        finally:
            cursor.close()

    def delete_playlist(self, playlist_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=?", (playlist_id,))
            cursor.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
            self.conn.commit()
            return "OK|Playlist deleted"
        finally:
            cursor.close()

    def add_songs_to_playlist(self, playlist_id, song_ids):
        cursor = self.conn.cursor()
        try:
            for s_id in song_ids:
                cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)", (playlist_id, s_id))
            self.conn.commit()
            return "OK|Songs added"
        except Exception as e:
            return f"ERROR|{str(e)}"
        finally:
            cursor.close()

    def add_single_song_to_playlist(self, playlist_id, song_id):
        """Adds exactly one song to a playlist. Used by the Search Page popup."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
                (playlist_id, song_id)
            )
            self.conn.commit()
            return "OK|Song added"
        except Exception as e:
            return f"ERROR|{str(e)}"
        finally:
            cursor.close()

    def get_playlist_songs(self, playlist_id):
        cursor = self.conn.cursor()
        try:
            # FIX: Added songs.cover_url to the SELECT statement
            cursor.execute("""
                SELECT songs.id, songs.title, songs.artist, songs.cover_url
                FROM songs
                JOIN playlist_songs ON songs.id = playlist_songs.song_id
                WHERE playlist_songs.playlist_id=?
            """, (playlist_id,))
            rows = cursor.fetchall()
            if rows:
                # FIX: Added "cover_url": r[3] to the dictionary
                songs = [
                    {
                        "id": r[0],
                        "title": r[1],
                        "artist": r[2],
                        "cover_url": r[3]
                    } for r in rows
                ]
                return f"OK|{json.dumps(songs)}"
            return "ERROR|No songs in playlist"
        finally:
            cursor.close()

    def update_playlist_cover(self, playlist_id, filename):
        """Updates the cover_url for a specific playlist."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE playlists SET cover_url=? WHERE id=?", (filename, playlist_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating playlist cover: {e}")
            return False
        finally:
            cursor.close()

    def remove_song_from_playlist(self, playlist_id, song_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=? AND song_id=?", (playlist_id, song_id))
            self.conn.commit()
            return "OK|Song removed from playlist"
        finally:
            cursor.close()

    def close(self):
        self.conn.close()