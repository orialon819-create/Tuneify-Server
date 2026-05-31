# admin_app.py

"""
Flask admin panel for Tuneify.
Admin uploads an audio file + metadata.
ML pipeline runs automatically to predict mood + confidence.
All fields saved to the songs table in tuneify.db.
"""

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "tuneify_admin_secret_2024"

# Config
DB_PATH       = "tuneify.db"
MUSIC_DIR     = "./music_library"
COVERS_DIR    = "./song_covers"
MODEL_PATH    = "ml/mood_model.pkl"
ENCODER_PATH  = "ml/label_encoder.pkl"
ALLOWED_AUDIO = {"mp3", "wav"}
ALLOWED_IMG   = {"jpg", "jpeg", "png"}

os.makedirs(MUSIC_DIR,  exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

ADMINS = {"admin": "tuneify26"}

from ml.predict import predict_mood


# Input: None
# Output: returns all songs from database

def get_all_songs() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT id, title, artist, file_name, stream_url,
                   mood, mood_score, lyrics, cover_url
            FROM songs ORDER BY id DESC
        """)
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


# Input: title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url
# Output: inserts song into database and returns inserted id

def insert_song(title, artist, file_name, stream_url,
                mood, mood_score, lyrics, cover_url) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO songs
                (title, artist, file_name, stream_url, mood, mood_score, lyrics, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, artist, file_name, stream_url,
              mood, round(mood_score, 3), lyrics, cover_url))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


# Input: song_id (int)
# Output: deletes song from database

def delete_song(song_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    try:
        cur.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        conn.commit()
    finally:
        cur.close(); conn.close()


# Input: None
# Output: redirects to dashboard or login page

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "admin" in session else url_for("login"))


# Input: username, password
# Output: logs admin in or returns error page

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if ADMINS.get(request.form.get("username")) == request.form.get("password"):
            session["admin"] = request.form.get("username")
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)


# Input: None
# Output: logs admin out

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# Input: None
# Output: displays dashboard page with songs

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html",
                           songs=get_all_songs(),
                           success=request.args.get("success"))


# Input: song_id (int)
# Output: deletes song and redirects

@app.route("/delete/<int:song_id>", methods=["POST"])
def delete(song_id):
    if "admin" not in session:
        return redirect(url_for("login"))
    delete_song(song_id)
    return redirect(url_for("dashboard"))


# Input: title, artist, lyrics, audio file, optional cover file
# Output: uploads song, runs ML prediction, saves to DB, returns result page

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("upload.html")

    title  = request.form.get("title",  "").strip()
    artist = request.form.get("artist", "").strip()
    lyrics = request.form.get("lyrics", "").strip()

    if not title or not artist:
        return render_template("upload.html",
                               error="Title and artist are required.")

    audio_file = request.files.get("audio")
    if not audio_file or audio_file.filename == "":
        return render_template("upload.html", error="Please upload an audio file.")

    ext = audio_file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_AUDIO:
        return render_template("upload.html",
                               error="Only .mp3 and .wav files are allowed.")

    file_name  = secure_filename(audio_file.filename)
    audio_path = os.path.join(MUSIC_DIR, file_name)
    audio_file.save(audio_path)
    stream_url = f"/TuneifyServer/music_library/{file_name}"

    cover_url  = ""
    cover_file = request.files.get("cover")
    if cover_file and cover_file.filename != "":
        cext = cover_file.filename.rsplit(".", 1)[-1].lower()
        if cext in ALLOWED_IMG:
            cover_name = secure_filename(cover_file.filename)
            cover_file.save(os.path.join(COVERS_DIR, cover_name))
            cover_url = f"/TuneifyServer/song_covers/{cover_name}"

    try:
        mood, confidence, features, all_probs = predict_mood(audio_path)
    except Exception as e:
        print(f"ML error: {e}")
        mood, confidence, features, all_probs = "Unknown", 0.0, {}, {}

    song_id = insert_song(
        title      = title,
        artist     = artist,
        file_name  = file_name,
        stream_url = stream_url,
        mood       = mood,
        mood_score = confidence,
        lyrics     = lyrics,
        cover_url  = cover_url
    )

    return render_template("result.html",
        title      = title,
        artist     = artist,
        file_name  = file_name,
        stream_url = stream_url,
        mood       = mood,
        confidence = round(confidence * 100, 1),
        mood_score = round(confidence, 3),
        features   = features,
        all_probs  = all_probs,
        lyrics     = lyrics,
        cover_url  = cover_url,
        song_id    = song_id
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)