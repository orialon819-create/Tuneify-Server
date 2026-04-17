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

        # Inside your Dispatcher's handle_command method:
        elif command == "UPDATE_PLAYLIST_COVER":
            playlist_id = params.get("playlist_id")
            filename = params.get("filename")

            # Call the service to update the DB
            return self.playlist_service.update_playlist_cover(playlist_id, filename)

        # Inside your server's command handler
        elif command == "GET_USER_PLAYLISTS":
            # 1. Get the user_id sent from the Android app
            user_id = params.get("user_id")

            # 2. Call the playlist_service to get the data from the DB
            # This calls the function we discussed earlier
            return self.playlist_service.get_user_playlists(user_id)

        elif command == "ADD_SONG_TO_PLAYLIST":
            # This handles the actual 'Save' action from the popup
            song_id = params.get("song_id")
            playlist_id = params.get("playlist_id")
            return self.playlist_service.add_single_song(playlist_id, song_id)

        elif command == "ADD_SONG_TO_PLAYLIST":
            # Android sends: params.put("song_id", song.id)
            s_id = params.get("song_id")
            p_id = params.get("playlist_id")

            # We call the single song version
            return self.playlist_service.add_single_song(p_id, s_id)

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
                    return f"OK|{new_playlist_id}"
                except (IndexError, ValueError):
                    return "ERROR|Failed to parse new playlist ID"

            return result
        # ---------- UNKNOWN ----------
        else:
            return "ERROR|Unknown command"