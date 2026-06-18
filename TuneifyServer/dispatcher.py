import json


"""
dispatcher.py

Routes parsed client commands to the appropriate service layer.

Acts as the central communication router between the client and backend services
(user, song, and playlist services). Each command is mapped to a specific handler.
"""


class Dispatcher:

    # Initializes dispatcher with system services
    # Input: user_service, song_service, playlist_service (service objects)
    # Output: None
    def __init__(self, user_service, song_service, playlist_service) -> None:
        self.user_service = user_service
        self.song_service = song_service
        self.playlist_service = playlist_service

    # Main routing function for all client commands
    # Input: parsed_message (dict containing command + parameters)
    # Output: response string (str in format OK|... or ERROR|...)
    def dispatch(self, parsed_message: dict) -> str:

        command = parsed_message.get("command", "").upper()
        params = parsed_message.get("parameters", {})

        # USER COMMANDS ─────────────────────────────────────────────

        # Registers a new user
        # Input: first_name, last_name, email, username, password
        # Output: status string
        if command == "REGISTER":
            return self.user_service.register(
                params.get("first_name"), params.get("last_name"),
                params.get("email"), params.get("username"),
                params.get("password")
            )

        # Logs user into system
        # Input: username, password
        # Output: status string
        elif command == "LOGIN":
            return self.user_service.login(
                params.get("username"), params.get("password")
            )

        # Sends password reset code to user email
        # Input: email
        # Output: status string (success/error)
        elif command == "REQUEST_RESET":
            return self.user_service.generate_reset_code(params.get("email"))

        # Verifies reset code and updates password
        # Input: email, code, new_password
        # Output: status string
        elif command == "VERIFY_RESET":
            return self.user_service.verify_and_update_password(
                params.get("email"), params.get("code"), params.get("new_password")
            )

        # SONG COMMANDS ─────────────────────────────────────────────

        # Gets all songs from database
        # Input: none
        # Output: JSON string containing list of songs
        elif command == "GET_ALL_SONGS":
            data = self.song_service.get_all_songs()
            return f"OK|{json.dumps(data)}"

        # Searches songs by query (title or artist match)
        # Input: query (str)
        # Output: search results string
        elif command == "SEARCH_SONGS":
            return self.song_service.search_songs(params.get("query", ""))

        # Gets one song by mood
        # Input: mood (str)
        # Output: stream URL or error string
        elif command == "GET_SONG_BY_MOOD":
            mood = params.get("mood", "Happy")
            try:
                url = self.song_service.get_song_by_mood(mood)
                return f"OK|{url}" if url else "ERROR|No song found"
            except Exception as e:
                return f"ERROR|{e}"

        # PLAYLIST COMMANDS ─────────────────────────────────────────

        # Creates new playlist and optionally adds songs
        # Input: user_id, playlist_name, songs (list of song IDs)
        # Output: playlist id or error string
        elif command == "CREATE_PLAYLIST":
            u_id = params.get("user_id")
            name = params.get("playlist_name")
            song_ids = params.get("songs", [])

            result = self.playlist_service.create_playlist(u_id, name)

            if result.startswith("OK"):
                try:
                    new_id = int(result.split("|")[1])
                    self.playlist_service.add_songs(new_id, song_ids)
                    return f"OK|{new_id}"
                except (IndexError, ValueError):
                    return "ERROR|Failed to parse new playlist ID"

            return result

        # Gets all playlists of a user
        # Input: user_id
        # Output: JSON list of playlists
        elif command == "GET_USER_PLAYLISTS":
            return self.playlist_service.get_user_playlists(params.get("user_id"))

        # Gets songs inside a playlist
        # Input: playlist_id
        # Output: JSON list of songs
        elif command == "GET_PLAYLIST_SONGS":
            return self.playlist_service.get_songs(params.get("playlist_id"))

        # Gets songs filtered by mood (multiple results)
        # Input: mood, count
        # Output: JSON songs
        elif command == "GET_SONGS_BY_MOOD_LIST":
            mood = params.get("mood", "Happy")
            count = int(params.get("count", 5))
            return self.song_service.get_songs_by_mood_list(mood, count)

        # Gets number of songs in playlist
        # Input: playlist_id
        # Output: count string
        elif command == "GET_PLAYLIST_SONG_COUNT":
            return self.playlist_service.get_song_count(params.get("playlist_id"))

        # Adds a single song to playlist
        # Input: playlist_id, song_id
        # Output: status string
        elif command == "ADD_SONG_TO_PLAYLIST":
            return self.playlist_service.add_single_song(
                params.get("playlist_id"), params.get("song_id")
            )

        # Removes song from playlist
        # Input: playlist_id, song_id
        # Output: status string
        elif command == "REMOVE_SONG_FROM_PLAYLIST":
            return self.playlist_service.remove_song(
                params.get("playlist_id"), params.get("song_id")
            )

        # Updates playlist name
        # Input: playlist_id, new_name
        # Output: status string
        elif command == "UPDATE_PLAYLIST_NAME":
            return self.playlist_service.update_name(
                params.get("playlist_id"), params.get("new_name")
            )

        # Updates playlist cover image
        # Input: playlist_id, filename
        # Output: status string
        elif command == "UPDATE_PLAYLIST_COVER":
            return self.playlist_service.update_playlist_cover(
                params.get("playlist_id"), params.get("filename")
            )

        # Gets recommended playlists ("For You")
        # Input: user_id
        # Output: JSON playlists
        elif command == "GET_FOR_YOU_PLAYLISTS":
            return self.playlist_service.get_for_you_playlists(params.get("user_id"))

        # Deletes a playlist
        # Input: playlist_id
        # Output: status string
        elif command == "DELETE_PLAYLIST":
            return self.playlist_service.delete_playlist(params.get("playlist_id"))

        # Gets or creates liked songs playlist
        # Input: user_id
        # Output: playlist id string
        elif command == "GET_OR_CREATE_LIKED_SONGS":
            return self.playlist_service.get_or_create_liked_songs(params.get("user_id"))

        # UNKNOWN COMMAND ─────────────────────────────────────────────

        # Input: unrecognized command
        # Output: error string
        else:
            return "ERROR|Unknown command"