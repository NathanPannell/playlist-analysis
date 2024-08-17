from flask import request, jsonify, session
from config import app, get_db_connection
import models
import requests
import time
from os import environ


def chunked_list(items, chunk_size=100):
    items = list(items)
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def get_spotify_token_headers():
    now = time.time()
    if "spotify_token" not in session or session["spotify_token_expiry"] < now:
        # Token is missing or expired, get a new one
        auth_url = "https://accounts.spotify.com/api/token"
        auth_response = requests.post(
            auth_url,
            {
                "grant_type": "client_credentials",
                "client_id": environ.get("SPOTIFY_CLIENT_ID"),
                "client_secret": environ.get("SPOTIFY_CLIENT_SECRET"),
            },
        )
        auth_response_data = auth_response.json()

        print(f"Generated a new token: {auth_response_data['access_token']}")

        # Set token expiry early to refresh before it errors out
        session["spotify_token_expiry"] = now + auth_response_data["expires_in"] - 60
        session["spotify_token"] = auth_response_data["access_token"]

    return {"Authorization": f"Bearer {session['spotify_token']}"}


def fetch_playlist_data(playlist_id):
    print(f"Fetching playlist: {playlist_id}")

    return requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers=get_spotify_token_headers(),
    ).json()


def update_or_create_playlist(conn, playlist):
    images = playlist.get("images")
    thumbnail = images[0].get("url") if images else None

    playlist_data = {
        "id": playlist.get("id"),
        "name": playlist.get("name"),
        "description": playlist.get("description"),
        "thumbnail": thumbnail,
        "followers_count": playlist.get("followers", {}).get("total"),
    }

    models.insert_or_update_playlist(conn, playlist_data)


def fetch_tracks(playlist):
    all_tracks = []
    next_tracks = playlist.get("tracks", {})
    tracks = [track["track"] for track in playlist.get("tracks", {}).get("items", [])]

    while tracks:
        all_tracks.extend(tracks)
        next_tracks_url = next_tracks.get("next")
        if not next_tracks_url:
            break

        print("Getting another batch of 100 tracks")

        next_tracks = requests.get(
            next_tracks_url, headers=get_spotify_token_headers()
        ).json()
        tracks = [track["track"] for track in next_tracks.get("items", [])]

    return all_tracks


def update_or_create_tracks(conn, all_tracks):
    all_track_ids = {track["id"] for track in all_tracks}

    for tracks, track_ids in zip(chunked_list(all_tracks), chunked_list(all_track_ids)):
        print(f"Getting a batch of {len(track_ids)} tracks' audio features")

        tracks_features = requests.get(
            "https://api.spotify.com/v1/audio-features",
            params={"ids": ",".join(track_ids)},
            headers=get_spotify_token_headers(),
        ).json()["audio_features"]

        print(len(tracks_features))

        for track, track_features in zip(tracks, tracks_features):
            track_features = track_features or {}
            images = track.get("album", {}).get("images")
            thumbnail = images[0].get("url") if images else None
            track_data = {
                "id": track.get("id"),
                "name": track.get("name"),
                "thumbnail": thumbnail,
                "preview_url": track.get("preview_url"),
                "popularity": track.get("popularity"),
                "danceability": track_features.get("danceability"),
                "energy": track_features.get("energy"),
                "loudness": track_features.get("loudness"),
                "speechiness": track_features.get("speechiness"),
                "acousticness": track_features.get("acousticness"),
                "instrumentalness": track_features.get("instrumentalness"),
                "liveness": track_features.get("liveness"),
                "valence": track_features.get("valence"),
                "tempo": track_features.get("tempo"),
                "mode": track_features.get("mode"),
                "duration_ms": track.get("duration_ms"),
            }

            models.insert_or_update_track(conn, track_data)


def update_or_create_artists(conn, all_tracks):
    all_artists_ids = {
        artist["id"] for track in all_tracks for artist in track["artists"]
    }

    for artists_ids in chunked_list(all_artists_ids, 50):
        print(f"Getting a batch of {len(artists_ids)} artists")

        artists = requests.get(
            "https://api.spotify.com/v1/artists",
            params={"ids": ",".join(artists_ids)},
            headers=get_spotify_token_headers(),
        ).json()["artists"]

        for artist_id, artist in zip(artists_ids, artists):
            images = artist.get("images")
            thumbnail = images[0].get("url") if images else None
            artist_data = {
                "id": artist.get("id"),
                "name": artist.get("name"),
                "thumbnail": thumbnail,
                "popularity": artist.get("popularity"),
            }
            models.insert_or_update_artist(conn, artist_data)

            for genre in artist.get("genres", []):
                models.insert_artist_genre(conn, artist_id, genre)

            for track in all_tracks:
                if artist_id in [a["id"] for a in track["artists"]]:
                    models.insert_artist_track(conn, artist_id, track["id"])


@app.route("/sync_playlist", methods=["POST"])
def sync_playlist():
    # try:
    url = request.json.get("url")
    print(f"Syncing on url: {url}")

    playlist_id = url.split("/")[-1].split("?")[0]

    conn = get_db_connection()
    playlist = fetch_playlist_data(playlist_id)
    update_or_create_playlist(conn, playlist)

    all_tracks = fetch_tracks(playlist)
    update_or_create_tracks(conn, all_tracks)
    update_or_create_artists(conn, all_tracks)

    conn.close()

    return (
        jsonify(
            {
                "message": f"Playlist ({playlist.get('name', 'Untitled')}) synced to database"
            }
        ),
        201,
    )


# except Exception as e:
#     print(e)
#     return jsonify({"message": str(e)}), 500


@app.route("/playlists", methods=["GET"])
def get_all_playlists():
    conn = get_db_connection()
    playlists = models.get_all_playlists(conn)
    conn.close()
    return jsonify(playlists)


@app.route("/tracks", methods=["GET"])
def get_all_tracks():
    conn = get_db_connection()
    tracks = models.get_all_tracks(conn)
    conn.close()
    return jsonify(tracks)


@app.route("/artists", methods=["GET"])
def get_all_artists():
    conn = get_db_connection()
    artists = models.get_all_artists(conn)
    conn.close()
    return jsonify(artists)


@app.route("/reset", methods=["DELETE"])
def reset_database():
    conn = get_db_connection()
    models.create_tables(conn)
    conn.close()
    return jsonify({"message": "Database has been reset."}), 200


if __name__ == "__main__":
    conn = get_db_connection()
    models.create_tables(conn)
    conn.close()
    app.run(debug=True)
