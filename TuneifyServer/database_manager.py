# database_manager.py

"""
Provides database management utilities for the Tuneify system.

Handles:
- User registration and authentication
- Secure password storage (PBKDF2 + salt + pepper)
- Song retrieval and search
- Playlist creation and management
- User data updates

All functions interact with an SQLite database and return
formatted server responses: "OK|..." or "ERROR|...".
"""

import sqlite3
import hashlib
import json
from crypto_utils import hash_password, verify_password


class DatabaseManager:

    # Input: db_file (str)
    # Output: None
    # Initializes SQLite database connection
    def __init__(self, db_file) -> None:
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

    # Input: first_name (str), last_name (str), email (str), username (str), password (str)
    # Output: "OK|..." if success or "ERROR|..." if failure
    # Registers a new user with secure password hashing (PBKDF2 + salt + pepper)
    def add_user(self, first_name, last_name, email, username, password):
        cursor = self.conn.cursor()
        try:
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return "ERROR|User already exists"

            # Hash password securely
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

    # Input: username (str)
    # Output: "OK|{user_json}" or "ERROR|User not found"
    # Retrieves basic user information by username
    def get_user(self, username) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, first_name, last_name, email, username
                FROM users
                WHERE username=?
            """, (username,))

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

    # Input: username (str), password (str)
    # Output: "OK|{user_json}" or "ERROR|Invalid credentials"
    # Verifies login credentials using stored hash + salt
    def verify_user(self, username, password):
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

    # Input: email (str)
    # Output: row tuple or None
    # Retrieves user ID by email
    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE email=?",
                (email,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    # Input: username (str), field (str), new_value (str)
    # Output: "OK|..." or "ERROR|..."
    # Updates allowed user profile fields safely (SQL injection protected via whitelist)
    def update_user_field(self, username, field, new_value):
        cursor = self.conn.cursor()
        try:
            ALLOWED_FIELDS = {
                "first_name": "first_name",
                "last_name": "last_name",
                "email": "email"
            }

            safe_field = ALLOWED_FIELDS.get(field)
            if not safe_field:
                return "ERROR|Invalid field"

            cursor.execute(
                f"UPDATE users SET {safe_field} = ? WHERE username = ?",
                (new_value, username)
            )

            self.conn.commit()
            return "OK|Update successful"

        finally:
            cursor.close()

    # Input: query (str)
    # Output: "OK|[songs_json]" or "ERROR|No songs found"
    # Searches songs by title or artist
    def search_songs(self, query):
        cursor = self.conn.cursor()
        try:
            like = f"%{query}%"

            cursor.execute("""
                   SELECT id, title, artist, cover_url
                   FROM songs
                   WHERE title LIKE ? OR artist LIKE ?
               """, (like, like))

            results = cursor.fetchall()

            if results:
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

    # Input: None
    # Output: "OK|[songs_json]"
    # Retrieves all songs from database
    def get_all_songs(self) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, title, artist, file_name, stream_url,
                       mood, mood_score, lyrics, cover_url
                FROM songs
            """)

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

    # Input: mood (str), count (int)
    # Output: "OK|[songs_json]" or "ERROR|No songs found"
    # Returns random songs matching a mood
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

    # Input: mood (str)
    # Output: "OK|stream_url" or "ERROR|No song found"
    # Returns a single song stream URL for a mood
    def get_songs_by_mood(self, mood) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT stream_url FROM songs WHERE mood=? LIMIT 1",
                (mood,)
            )

            row = cursor.fetchone()
            return f"OK|{row[0]}" if row else "ERROR|No song found"

        finally:
            cursor.close()

    # Input: user_id (int), playlist_name (str)
    # Output: "OK|playlist_id" or "ERROR|..."
    # Creates a new playlist
    def create_playlist(self, user_id, playlist_name) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO playlists (name, user_id) VALUES (?, ?)",
                (playlist_name, user_id)
            )

            self.conn.commit()
            return f"OK|{cursor.lastrowid}"

        except Exception as e:
            return f"ERROR|{str(e)}"

        finally:
            cursor.close()

    # Input: user_id (int)
    # Output: "OK|[playlists_json]"
    # Retrieves all playlists for a user
    def get_user_playlists(self, user_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, name, user_id, cover_url
                FROM playlists
                WHERE user_id=?
            """, (user_id,))

            rows = cursor.fetchall()

            playlists = [
                {"id": r[0], "name": r[1], "user_id": r[2], "cover_url": r[3]}
                for r in rows
            ]

            return f"OK|{json.dumps(playlists)}"

        finally:
            cursor.close()

    # Input: playlist_id (int), new_name (str)
    # Output: "OK|Playlist updated"
    # Updates playlist name
    def update_playlist_name(self, playlist_id, new_name) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE playlists SET name=? WHERE id=?",
                (new_name, playlist_id)
            )

            self.conn.commit()
            return "OK|Playlist updated"

        finally:
            cursor.close()

    # Input: playlist_id (int)
    # Output: "OK|Playlist deleted"
    # Deletes playlist and its song relations
    def delete_playlist(self, playlist_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM playlist_songs WHERE playlist_id=?",
                (playlist_id,)
            )
            cursor.execute(
                "DELETE FROM playlists WHERE id=?",
                (playlist_id,)
            )

            self.conn.commit()
            return "OK|Playlist deleted"

        finally:
            cursor.close()

    # Input: playlist_id (int), song_ids (list)
    # Output: "OK|Songs added" or "ERROR|..."
    # Adds multiple songs to a playlist
    def add_songs_to_playlist(self, playlist_id, song_ids) -> str:
        cursor = self.conn.cursor()
        try:
            for s_id in song_ids:
                cursor.execute(
                    "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
                    (playlist_id, s_id)
                )

            self.conn.commit()
            return "OK|Songs added"

        except Exception as e:
            return f"ERROR|{str(e)}"

        finally:
            cursor.close()

    # Input: playlist_id (int), song_id (int)
    # Output: "OK|Song added" or "ERROR|..."
    # Adds a single song to a playlist
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

    # Input: playlist_id (int)
    # Output: "OK|[songs_json]" or "ERROR|No songs in playlist"
    # Retrieves all songs inside a playlist
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

    # Input: playlist_id (int), filename (str)
    # Output: True/False
    # Updates playlist cover image
    def update_playlist_cover(self, playlist_id, filename) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE playlists SET cover_url=? WHERE id=?",
                (filename, playlist_id)
            )

            self.conn.commit()
            return True

        except Exception:
            return False

        finally:
            cursor.close()

    # Input: playlist_id (int), song_id (int)
    # Output: "OK|Song removed from playlist"
    # Removes a song from a playlist
    def remove_song_from_playlist(self, playlist_id, song_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM playlist_songs WHERE playlist_id=? AND song_id=?",
                (playlist_id, song_id)
            )

            self.conn.commit()
            return "OK|Song removed from playlist"

        finally:
            cursor.close()

    # Input: playlist_id (int)
    # Output: "OK|count"
    # Returns number of songs in a playlist
    def get_playlist_song_count(self, playlist_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM playlist_songs WHERE playlist_id=?",
                (playlist_id,)
            )

            count = cursor.fetchone()[0]
            return f"OK|{count}"

        finally:
            cursor.close()

    # Input: user_id (int)
    # Output: "OK|[playlists_json]"
    # Returns recommended playlists for user
    def get_for_you_playlists(self, user_id) -> str:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, name, cover_url
                FROM playlists
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

    # Input: user_id (int)
    # Output: "OK|playlist_id" or "ERROR|..."
    # Gets or creates a "Liked Songs" playlist for a user
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

    # Input: None
    # Output: None
    # Closes database connection
    def close(self) -> None:
        self.conn.close()