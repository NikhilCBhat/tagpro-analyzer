import json
import spotipy
import spotipy.util as util
from collections import Counter

def get_spotify_api_object(username = "nikhil_bhat"):
    scope = 'user-read-recently-played'
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)
    return sp

def get_recent_spotify_songs(num_songs=50):
    sp = get_spotify_api_object()
    return sp.current_user_recently_played(limit=num_songs)

def get_song_genres():
    sp = get_spotify_api_object()
    recents = get_recent_spotify_songs()
    genre_counts = Counter()

    for song in recents["items"]:
        album = sp.album(song["track"]["album"]["id"])
        genres = album["genres"]
        if genres:
            print("Album has genres")
            for genre in genres:
                genre_counts[genre] += 1
        else:
            for artist in song["track"]["artists"]:
                sp_artist = sp.artist(artist["id"])
                for genre in sp_artist["genres"]:
                    genre_counts[genre] += 1

def get_genres(track_id=None, track_object=None):
    sp = get_spotify_api_object()
    if not track_object:
        track_object = sp.track(track_id)

    album_genres = sp.album(track_object["album"]["id"])["genres"]
    if album_genres:
        return album_genres

    artist_genres = []
    for artist in track_object["artists"]:
        sp_artist = sp.artist(artist["id"])
        artist_genres.extend(sp_artist["genres"])

    return artist_genres

def save_songs():
    songs = get_recent_spotify_songs()
    with open("spotify.json", "w") as f:
        json.dump(songs, f)