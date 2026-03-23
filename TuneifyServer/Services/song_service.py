"""
song_service.py

This service handles song-related operations: retrieving all songs,
searching songs by name or artist, and filtering songs by mood.
"""

from Services.find_ip import SERVER_IP, STREAM_PORT

class SongService:
    def __init__(self, db_manager):
        self.db = db_manager

    # Finds a song path in the DB and converts it into a streamable URL that the Android can play over the network
    def handle_get_song(self, mood):
        path = self.db.get_songs_by_mood(mood)
        # path = "/TuneifyServer/music_library/happy1.mp3"

        if path:
            # Constructs the full network address using the auto-detected Server IP
            full_url = f"http://{SERVER_IP}:{STREAM_PORT}{path}"
            return full_url

        return None

    # Executes a flexible search across the song library based on a text query
    def search_songs(self, query):
        return self.db.search_songs(query)

    # Retrieves a list of songs filtered by a specific mood category (e.g., 'Happy', 'Sad')
    def get_songs_by_mood(self, mood):
        return self.db.get_songs_by_mood(mood)

