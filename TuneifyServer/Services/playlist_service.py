#playlist_service.py

"""
Handles all playlist business logic and acts as a service layer
between the application and the database.
"""

class PlaylistService:
    def __init__(self, db):
        self.db = db

    # Input: user_id (int), name (str)
    # Output: Creates a new playlist

    def create_playlist(self, user_id, name) -> object:
        return self.db.create_playlist(user_id, name)

    # Input: user_id (int)
    # Output: Returns list of user playlists

    def get_user_playlists(self, user_id) -> list:
        return self.db.get_user_playlists(user_id)

    # Input: playlist_id (int)
    # Output: Returns list of songs in playlist

    def get_songs(self, playlist_id) -> list:
        return self.db.get_playlist_songs(playlist_id)

    # Input: user_id (int)
    # Output: Returns "For You" playlists

    def get_for_you_playlists(self, user_id) -> list:
        return self.db.get_for_you_playlists(user_id)

    # Input: playlist_id (int)
    # Output: Returns number of songs in playlist

    def get_song_count(self, playlist_id) -> int:
        return self.db.get_playlist_song_count(playlist_id)

    # Input: playlist_id (int), song_ids (list[int])
    # Output: Adds multiple songs to playlist

    def add_songs(self, playlist_id, song_ids) -> bool:
        return self.db.add_songs_to_playlist(playlist_id, song_ids)

    # Input: playlist_id (int), song_id (int)
    # Output: Adds single song to playlist

    def add_single_song(self, playlist_id, song_id) -> bool:
        return self.db.add_single_song_to_playlist(playlist_id, song_id)

    # Input: playlist_id (int), song_id (int)
    # Output: Removes song from playlist

    def remove_song(self, playlist_id, song_id) -> bool:
        return self.db.remove_song_from_playlist(playlist_id, song_id)

    # Input: playlist_id (int), new_name (str)
    # Output: Updates playlist name

    def update_name(self, playlist_id, new_name) -> bool:
        return self.db.update_playlist_name(playlist_id, new_name)

    # Input: playlist_id (int), filename (str)
    # Output: Returns success/failure message for cover update

    def update_playlist_cover(self, playlist_id, filename) -> str:
        success = self.db.update_playlist_cover(playlist_id, filename)
        return "OK|Cover updated" if success else "ERROR|Failed to update cover"

    # Input: playlist_id (int)
    # Output: Deletes playlist

    def delete_playlist(self, playlist_id) -> bool:
        return self.db.delete_playlist(playlist_id)

    # Input: user_id (int)
    # Output: Returns or creates "Liked Songs" playlist id

    def get_or_create_liked_songs(self, user_id) -> int:
        return self.db.get_or_create_liked_songs_playlist(user_id)