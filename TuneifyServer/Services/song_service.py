#song_service.py

"""
This service handles song-related operations: retrieving all songs,
searching songs by name or artist, and filtering songs by mood.
"""

from Services.find_ip import SERVER_IP, STREAM_PORT


class SongService:
    def __init__(self, db_manager):
        self.db = db_manager

    # Input: mood (str)
    # Output: Returns streamable song URL or None

    def handle_get_song(self, mood) -> str:

        path = self.db.get_songs_by_mood(mood)
        # path example: "/TuneifyServer/music_library/happy1.mp3"

        if path:
            # Constructs full network URL for Android streaming
            full_url = f"http://{SERVER_IP}:{STREAM_PORT}{path}"
            return full_url

        return None

    # Input: query (str)
    # Output: Returns list of songs matching search query

    def search_songs(self, query) -> list:
        return self.db.search_songs(query)

    # Input: mood (str), count (int)
    # Output: Returns list of songs filtered by mood (limited count)

    def get_songs_by_mood_list(self, mood: str, count: int = 5) -> list:
        return self.db.get_songs_by_mood_list(mood, count)

    # Input: mood (str)
    # Output: Returns single song

    def get_song_by_mood(self, mood) -> str:
        return self.db.get_song_by_mood(mood)