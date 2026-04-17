"""
playlist_service.py

This service handles playlist operations: creating playlists,
getting user playlists, updating playlist names, deleting playlists,
adding/removing songs, and retrieving songs in a playlist.
"""

class PlaylistService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_playlist(self, user_id, playlist_name):
        return self.db.create_playlist(user_id, playlist_name)

    # UPDATED: Now calls the DB Manager instead of running SQL here
    def update_playlist_cover(self, playlist_id, filename):
        success = self.db.update_playlist_cover(playlist_id, filename)
        if success:
            return "OK|Cover updated successfully"
        else:
            return "ERROR|Failed to update cover in database"

    # IMPORTANT: Ensure your DatabaseManager.get_user_playlists(user_id)
    # now includes the 'cover_url' column in its SELECT statement!
    def get_user_playlists(self, user_id):
        return self.db.get_user_playlists(user_id)

    def update_name(self, playlist_id, new_name):
        return self.db.update_playlist_name(playlist_id, new_name)

    def delete_playlist(self, playlist_id):
        return self.db.delete_playlist(playlist_id)

    def add_songs(self, playlist_id, song_ids):
        return self.db.add_songs_to_playlist(playlist_id, song_ids)

    def remove_song(self, playlist_id, song_id):
        return self.db.remove_song_from_playlist(playlist_id, song_id)

    def get_songs(self, playlist_id):
        return self.db.get_playlist_songs(playlist_id)

    def add_single_song(self, playlist_id, song_id):
        return self.db.add_single_song_to_playlist(playlist_id, song_id)