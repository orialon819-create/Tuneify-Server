"""
playlist_service.py
Handles all playlist business logic.
"""

class PlaylistService:
    def __init__(self, db):
        self.db = db

    def create_playlist(self, user_id, name):
        return self.db.create_playlist(user_id, name)

    def get_user_playlists(self, user_id):
        return self.db.get_user_playlists(user_id)

    def get_songs(self, playlist_id):
        return self.db.get_playlist_songs(playlist_id)

    def get_for_you_playlists(self, user_id):
        return self.db.get_for_you_playlists(user_id)

    def get_song_count(self, playlist_id):
        return self.db.get_playlist_song_count(playlist_id)

    def add_songs(self, playlist_id, song_ids):
        return self.db.add_songs_to_playlist(playlist_id, song_ids)

    def add_single_song(self, playlist_id, song_id):
        return self.db.add_single_song_to_playlist(playlist_id, song_id)

    def remove_song(self, playlist_id, song_id):
        return self.db.remove_song_from_playlist(playlist_id, song_id)

    def update_name(self, playlist_id, new_name):
        return self.db.update_playlist_name(playlist_id, new_name)

    def update_playlist_cover(self, playlist_id, filename):
        success = self.db.update_playlist_cover(playlist_id, filename)
        return "OK|Cover updated" if success else "ERROR|Failed to update cover"

    def delete_playlist(self, playlist_id):
        return self.db.delete_playlist(playlist_id)

    def get_or_create_liked_songs(self, user_id):
        """Returns the Liked Songs playlist id for this user, creating it if needed."""
        return self.db.get_or_create_liked_songs_playlist(user_id)