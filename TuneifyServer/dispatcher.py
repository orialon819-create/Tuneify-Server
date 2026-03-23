"""
dispatcher.py

The Dispatcher receives parsed client commands from ClientHandler
and routes them to the appropriate service.
"""
import json

class Dispatcher:
    def __init__(self, user_service, song_service, playlist_service):
        self.user_service = user_service
        self.song_service = song_service
        self.playlist_service = playlist_service

    def dispatch(self, parsed_message: dict) -> str:
        # Command from Android is usually uppercase
        command = parsed_message.get("command", "").upper()
        # parameters is the JSONObject we sent from Android
        params = parsed_message.get("parameters", {})

        # ---------- USER COMMANDS ----------
        if command == "REGISTER":
            return self.user_service.register(
                params.get("first_name"),
                params.get("last_name"),
                params.get("email"),
                params.get("username"),
                params.get("password")
            )

        elif command == "LOGIN":
            return self.user_service.login(
                params.get("username"),
                params.get("password")
            )

        # ---------- FORGOT PASSWORD COMMANDS ----------
        elif command == "REQUEST_RESET":
            email = params.get("email")
            return self.user_service.generate_reset_code(email)

        elif command == "VERIFY_RESET":
            email = params.get("email")
            code = params.get("code")
            new_pass = params.get("new_password")
            return self.user_service.verify_and_update_password(email, code, new_pass)

        # ---------- SONG COMMANDS ----------
        elif command == "GET_ALL_SONGS":
            # Assuming song_service returns a list of dictionaries
            data = self.song_service.get_all_songs()
            return f"OK|{json.dumps(data)}"

        elif command == "SEARCH_SONGS":
            # FIX: Get 'query' from the params dictionary
            query = params.get("query", "")
            data = self.song_service.search_songs(query)
            # If your service already returns "OK|json", just return data.
            # If it returns a list, use: return f"OK|{json.dumps(data)}"
            return data

        elif command == "GET_SONGS_BY_MOOD":
            # FIX: Look for the 'mood' key sent by Android
            mood = params.get("mood", "Happy")

            try:
                url = self.song_service.handle_get_song(mood)
                if url:
                    return f"OK|{url}"
                else:
                    return "ERROR|No song found"
            except Exception as e:
                print(f"DEBUG: Error -> {e}")
                return "ERROR|Server Error"

        # ---------- PLAYLIST COMMANDS ----------
        elif command == "GET_PLAYLIST_SONGS":
            # FIX: Get playlist_id from params
            p_id = params.get("playlist_id")
            data = self.playlist_service.get_songs(p_id)
            return f"OK|{json.dumps(data)}"

        elif command == "CREATE_PLAYLIST":
            u_id = params.get("user_id")
            name = params.get("playlist_name")
            song_ids = params.get("songs", [])

            # 1. Create the playlist record
            result = self.playlist_service.create_playlist(u_id, name)

            if result.startswith("OK"):
                # Get the ID from the "OK|ID" string
                try:
                    new_playlist_id = int(result.split("|")[1])
                    # 2. Link the songs to that new ID
                    self.playlist_service.add_songs(new_playlist_id, song_ids)
                    return "OK|Playlist created with songs"
                except (IndexError, ValueError):
                    return "ERROR|Failed to parse new playlist ID"

            return result # Return the error from create_playlist if it failed

        # ---------- UNKNOWN ----------
        else:
            return "ERROR|Unknown command"