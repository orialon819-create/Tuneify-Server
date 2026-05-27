import sqlite3
import hashlib
import json
from crypto_utils import hash_password, verify_password

"""
database_manager.py

Handles all database operations for the Tuneify system.
Includes user management, song retrieval, and playlist operations.

Each function interacts directly with the SQLite database and returns
formatted responses for the server (OK|... / ERROR|...).
"""
class DatabaseManager:

    # Initializes database connection
    # Input: db_file (str)
    # Output: None
    def __init__(self, db_file) -> None:
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

    # Adds a new user to database
    # Input: first name, last name, email, username and password
    # Output: status message (str)
    def add_user(self, first_name, last_name, email, username, password):
        """
        Registers a new user.
        Password is hashed with PBKDF2-HMAC-SHA256 + salt + pepper.
        NEVER stores the plaintext password.
        """
        cursor = self.conn.cursor()
        try:
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return "ERROR|User already exists"

            # Hash the password — returns (hash_hex, salt_hex)
            password_hash, salt = hash_password(password)

            cursor.execute("""
                   INSERT INTO users (first_name, last_name, email, username, password, salt)
                   VALUES (?, ?, ?, ?, ?, ?)
               """, (first_name, last_name, email, username, password_hash, salt))
            self.conn.commit()
            return "OK|User added successfully"

        except Exception as e:
            return f"ERROR|{e}"
        finally:
            cursor.close()

    # Retrieves user info by username
    # Input: username (str)
    # Output: JSON user or error
    def get_user(self, username) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, first_name, last_name, email, username FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user:
                user_data = {
                    "id": user[0],
                    "first_name": user[1],
                    "last_name": user[2],
                    "email": user[3],
                    "username": user[4]
                }
                return f"OK|{json.dumps(user_data)}"

            return "ERROR|User not found"
        finally:
            cursor.close()

    # Verifies user login credentials
    # Input: username, password (str)
    # Output: JSON user or error
    def verify_user(self, username, password):
        """
        Verifies login credentials.
        Fetches the stored hash and salt, then re-hashes the input to compare.
        Uses secrets.compare_digest to prevent timing attacks.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, first_name, last_name, email, username, password, salt
                FROM users WHERE username=?
            """, (username,))
            row = cursor.fetchone()

            if not row:
                return "ERROR|Invalid credentials"

            stored_hash = row[5]
            stored_salt = row[6]

            # Verify using PBKDF2 — same function used during registration
            if not verify_password(password, stored_hash, stored_salt):
                return "ERROR|Invalid credentials"

            import json
            user_data = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "username": row[4]
            }
            return f"OK|{json.dumps(user_data)}"

        finally:
            cursor.close()

    # Updates a user field
    # Input: username, field, new value (str)
    # Output: status message (str)
    def update_user_field(self, username, field, new_value):
        """
        Updates a specific user profile field.
        Uses a whitelist dict to prevent SQL injection —
        the field name never goes directly into the query string.
        """
        cursor = self.conn.cursor()
        try:
            # Whitelist: only these field names are allowed
            # This completely prevents SQL injection on this method
            ALLOWED_FIELDS = {
                "first_name": "first_name",
                "last_name": "last_name",
                "email": "email"
            }

            safe_field = ALLOWED_FIELDS.get(field)
            if not safe_field:
                return "ERROR|Invalid field"

            # safe_field is guaranteed to be one of the three above
            cursor.execute(
                f"UPDATE users SET {safe_field} = ? WHERE username = ?",
                (new_value, username)
            )
            self.conn.commit()
            return "OK|Update successful"

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

    # Gets all songs from database
    # Input: None
    # Output: JSON list of songs
    def get_all_songs(self) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url FROM songs")
            rows = cursor.fetchall()

            songs_list = []
            for r in rows:
                songs_list.append({
                    "id": r[0],
                    "title": r[1],
                    "artist": r[2],
                    "file_name": r[3],
                    "stream_url": r[4],
                    "mood": r[5],
                    "mood_score": r[6],
                    "lyrics": r[7],
                    "cover_url": r[8]
                })

            return f"OK|{json.dumps(songs_list)}"
        finally:
            cursor.close()

    # Gets random songs by mood
    # Input: mood (str), count (int)
    # Output: JSON songs or error
    def get_songs_by_mood_list(self, mood: str, count: int = 3) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, title, artist, cover_url
                FROM songs
                WHERE mood = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (mood, count))

            rows = cursor.fetchall()

            if not rows:
                return "ERROR|No songs found for this mood"

            songs = [
                {"id": r[0], "title": r[1], "artist": r[2], "cover_url": r[3]}
                for r in rows
            ]

            return f"OK|{json.dumps(songs)}"
        finally:
            cursor.close()

    # Gets one song stream URL by mood
    # Input: mood (str)
    # Output: stream URL or error
    def get_songs_by_mood(self, mood) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT stream_url FROM songs WHERE mood=? LIMIT 1", (mood,))
            row = cursor.fetchone()
            return f"OK|{row[0]}" if row else "ERROR|No song found"
        finally:
            cursor.close()

    # Creates playlist
    # Input: user id (int), playlist name (str)
    # Output: playlist id or error
    def create_playlist(self, user_id, playlist_name) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO playlists (name, user_id) VALUES (?, ?)", (playlist_name, user_id))
            self.conn.commit()
            return f"OK|{cursor.lastrowid}"
        except Exception as e:
            return f"ERROR|{str(e)}"
        finally:
            cursor.close()

    # Gets user playlists
    # Input: user id (int)
    # Output: JSON playlists
    def get_user_playlists(self, user_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, name, user_id, cover_url FROM playlists WHERE user_id=?", (user_id,))
            rows = cursor.fetchall()

            playlists = [{"id": r[0], "name": r[1], "user_id": r[2], "cover_url": r[3]} for r in rows]

            return f"OK|{json.dumps(playlists)}"
        finally:
            cursor.close()

    # Updates playlist name
    # Input: playlist id (int), new name (str)
    # Output: status message
    def update_playlist_name(self, playlist_id, new_name) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE playlists SET name=? WHERE id=?", (new_name, playlist_id))
            self.conn.commit()
            return "OK|Playlist updated"
        finally:
            cursor.close()

    # Deletes playlist
    # Input: playlist id (int)
    # Output: status message
    def delete_playlist(self, playlist_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=?", (playlist_id,))
            cursor.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
            self.conn.commit()
            return "OK|Playlist deleted"
        finally:
            cursor.close()

    # Adds multiple songs to playlist
    # Input: playlist id (int), song ids (list)
    # Output: status message
    def add_songs_to_playlist(self, playlist_id, song_ids) -> str:
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

    # Adds single song to playlist
    # Input: playlist id (int), song id (int)
    # Output: status message
    def add_single_song_to_playlist(self, playlist_id, song_id) -> str:
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

    # Gets songs in playlist
    # Input: playlist id (int)
    # Output: JSON songs or error
    def get_playlist_songs(self, playlist_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT songs.id, songs.title, songs.artist, songs.cover_url
                FROM songs
                JOIN playlist_songs ON songs.id = playlist_songs.song_id
                WHERE playlist_songs.playlist_id=?
            """, (playlist_id,))

            rows = cursor.fetchall()

            if rows:
                songs = [
                    {"id": r[0], "title": r[1], "artist": r[2], "cover_url": r[3]}
                    for r in rows
                ]
                return f"OK|{json.dumps(songs)}"

            return "ERROR|No songs in playlist"
        finally:
            cursor.close()

    # Updates playlist cover
    # Input: playlist id (int), filename (str)
    # Output: bool success
    def update_playlist_cover(self, playlist_id, filename) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE playlists SET cover_url=? WHERE id=?", (filename, playlist_id))
            self.conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()

    # Removes song from playlist
    # Input: playlist id (int), song id (int)
    # Output: status message
    def remove_song_from_playlist(self, playlist_id, song_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM playlist_songs WHERE playlist_id=? AND song_id=?", (playlist_id, song_id))
            self.conn.commit()
            return "OK|Song removed from playlist"
        finally:
            cursor.close()

    # Gets playlist song count
    # Input: playlist_id (int)
    # Output: count (int)
    def get_playlist_song_count(self, playlist_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM playlist_songs WHERE playlist_id=?", (playlist_id,))
            count = cursor.fetchone()[0]
            return f"OK|{count}"
        finally:
            cursor.close()

    # Gets for you playlists
    # Input: user id (int)
    # Output: JSON playlists
    def get_for_you_playlists(self, user_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, name, cover_url FROM playlists
                WHERE name IN ('Top Pop Hits', '80s Mix', 'Throwback Mix')
            """)
            rows = cursor.fetchall()

            playlists = [
                {"id": r[0], "name": r[1], "subtitle": "Recommended for you", "cover_url": r[2]}
                for r in rows
            ]

            return f"OK|{json.dumps(playlists)}"
        finally:
            cursor.close()

    # Gets or creates liked songs playlist
    # Input: user id (int)
    # Output: playlist id or error
    def get_or_create_liked_songs_playlist(self, user_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM playlists WHERE user_id=? AND name='Liked Songs'",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return f"OK|{row[0]}"

            cover_filename = "liked_songs_cover.png"

            cursor.execute("""
                INSERT INTO playlists (name, user_id, cover_url)
                VALUES ('Liked Songs', ?, ?)
            """, (user_id, cover_filename))

            self.conn.commit()
            return f"OK|{cursor.lastrowid}"

        except Exception as e:
            return f"ERROR|{e}"
        finally:
            cursor.close()

    # Closes database connection
    # Input: None
    # Output: None
    def close(self) -> None:
        self.conn.close()