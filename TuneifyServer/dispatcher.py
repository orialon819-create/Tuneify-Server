"""
dispatcher.py
Routes parsed client commands to the appropriate service.
"""
import json

class Dispatcher:
    def __init__(self, user_service, song_service, playlist_service):
        self.user_service = user_service
        self.song_service = song_service
        self.playlist_service = playlist_service

    def dispatch(self, parsed_message: dict) -> str:
        command = parsed_message.get("command", "").upper()
        params  = parsed_message.get("parameters", {})

        # ── USER ──────────────────────────────────────────────────────────────
        if command == "REGISTER":
            return self.user_service.register(
                params.get("first_name"), params.get("last_name"),
                params.get("email"),      params.get("username"),
                params.get("password")
            )

        elif command == "LOGIN":
            return self.user_service.login(
                params.get("username"), params.get("password")
            )

        elif command == "REQUEST_RESET":
            return self.user_service.generate_reset_code(params.get("email"))

        elif command == "VERIFY_RESET":
            return self.user_service.verify_and_update_password(
                params.get("email"), params.get("code"), params.get("new_password")
            )

        # ── SONGS ─────────────────────────────────────────────────────────────
        elif command == "GET_ALL_SONGS":
            data = self.song_service.get_all_songs()
            return f"OK|{json.dumps(data)}"

        elif command == "SEARCH_SONGS":
            return self.song_service.search_songs(params.get("query", ""))

        elif command == "GET_SONGS_BY_MOOD":
            mood = params.get("mood", "Happy")
            try:
                url = self.song_service.handle_get_song(mood)
                return f"OK|{url}" if url else "ERROR|No song found"
            except Exception as e:
                return f"ERROR|{e}"

        # ── PLAYLISTS ─────────────────────────────────────────────────────────
        elif command == "CREATE_PLAYLIST":
            u_id     = params.get("user_id")
            name     = params.get("playlist_name")
            song_ids = params.get("songs", [])
            result   = self.playlist_service.create_playlist(u_id, name)
            if result.startswith("OK"):
                try:
                    new_id = int(result.split("|")[1])
                    self.playlist_service.add_songs(new_id, song_ids)
                    return f"OK|{new_id}"
                except (IndexError, ValueError):
                    return "ERROR|Failed to parse new playlist ID"
            return result

        elif command == "GET_USER_PLAYLISTS":
            return self.playlist_service.get_user_playlists(params.get("user_id"))

        elif command == "GET_PLAYLIST_SONGS":
            return self.playlist_service.get_songs(params.get("playlist_id"))

        elif command == "GET_PLAYLIST_SONG_COUNT":
            return self.playlist_service.get_song_count(params.get("playlist_id"))

        elif command == "ADD_SONG_TO_PLAYLIST":
            return self.playlist_service.add_single_song(
                params.get("playlist_id"), params.get("song_id")
            )

        elif command == "REMOVE_SONG_FROM_PLAYLIST":
            return self.playlist_service.remove_song(
                params.get("playlist_id"), params.get("song_id")
            )

        elif command == "UPDATE_PLAYLIST_NAME":
            return self.playlist_service.update_name(
                params.get("playlist_id"), params.get("new_name")
            )

        elif command == "UPDATE_PLAYLIST_COVER":
            return self.playlist_service.update_playlist_cover(
                params.get("playlist_id"), params.get("filename")
            )


        elif command == "GET_FOR_YOU_PLAYLISTS":

            return self.playlist_service.get_for_you_playlists(params.get("user_id"))

        elif command == "DELETE_PLAYLIST":
            return self.playlist_service.delete_playlist(params.get("playlist_id"))

        elif command == "GET_OR_CREATE_LIKED_SONGS":
            return self.playlist_service.get_or_create_liked_songs(params.get("user_id"))

        # ── UNKNOWN ───────────────────────────────────────────────────────────
        else:
            return "ERROR|Unknown command"