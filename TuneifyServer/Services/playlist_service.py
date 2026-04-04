"""
playlist_service.py

This service handles playlist operations: creating playlists,
getting user playlists, updating playlist names, deleting playlists,
adding/removing songs, and retrieving songs in a playlist.
"""

class PlaylistService:
    def __init__(self, db_manager):
        self.db = db_manager

    # Takes a User ID and a playlist name string to register a new playlist in the system
    def create_playlist(self, user_id, playlist_name):
        return self.db.create_playlist(user_id, playlist_name)

    # Return all playlists associated with a specific user as a JSON string
    def get_user_playlists(self, user_id):
        return self.db.get_user_playlists(user_id)

    # Updates the name of an existing playlist, specifically changing its title
    def update_name(self, playlist_id, new_name):
        return self.db.update_playlist_name(playlist_id, new_name)

    # Completely removes a playlist record from the database using its unique ID
    def delete_playlist(self, playlist_id):
        return self.db.delete_playlist(playlist_id)

    # Links songs to a playlist by inserting their IDs into the relationship table
    def add_songs(self, playlist_id, song_ids):
        # DatabaseManager.add_songs_to_playlist returns "OK|..." or "ERROR|..."
        # We return that result directly to the dispatcher
        return self.db.add_songs_to_playlist(playlist_id, song_ids)

    # Breaks the link between a song and a playlist without deleting the actual song file
    def remove_song(self, playlist_id, song_id):
        return self.db.remove_song_from_playlist(playlist_id, song_id)

    # Returns a list of song objects currently contained within a specific playlist
    def get_songs(self, playlist_id):
        return self.db.get_playlist_songs(playlist_id)

    def add_single_song(self, playlist_id, song_id):
        return self.db.add_single_song_to_playlist(playlist_id, song_id)