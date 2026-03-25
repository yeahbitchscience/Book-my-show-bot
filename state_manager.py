import json
import os
import uuid

STATE_FILE = "seen_shows.json"
TRACKED_MOVIES_FILE = "tracked_movies.json"

# --- Seen Shows Logic ---
def load_seen_shows():
    if not os.path.exists(STATE_FILE):
        return []
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_seen_show(show_id):
    shows = load_seen_shows()
    if show_id not in shows:
        shows.append(show_id)
        with open(STATE_FILE, "w") as f:
            json.dump(shows, f, indent=4)
        return True
    return False

def is_show_seen(show_id):
    shows = load_seen_shows()
    return show_id in shows

# --- Tracked Movies Logic ---
def load_tracked_movies():
    if not os.path.exists(TRACKED_MOVIES_FILE):
        return {}
    try:
        with open(TRACKED_MOVIES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def add_tracked_movie(url, movie_format, added_by_chat_id):
    movies = load_tracked_movies()
    movie_id = str(uuid.uuid4())[:8]
    movies[movie_id] = {
        "url": url,
        "format": movie_format,
        "chat_id": added_by_chat_id
    }
    with open(TRACKED_MOVIES_FILE, "w") as f:
        json.dump(movies, f, indent=4)
    return movie_id

def remove_tracked_movie(movie_id):
    movies = load_tracked_movies()
    if movie_id in movies:
        del movies[movie_id]
        with open(TRACKED_MOVIES_FILE, "w") as f:
            json.dump(movies, f, indent=4)
        return True
    return False
