from flask import request, jsonify, session
from flask_cors import cross_origin
from collections import Counter
from config import app, get_db_connection
import models
import requests
import time
from os import environ


def chunked_list(items, chunk_size=100) -> iter:
    items = list(items)
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def get_spotify_token_headers() -> dict[str, str]:
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


def fetch_playlist(playlist_id: str) -> dict:
    print(f"Fetching playlist: {playlist_id}")

    return requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers=get_spotify_token_headers(),
    ).json()


def update_or_create_playlist(conn, playlist: dict):
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

    return playlist_data


def fetch_all_playlist_tracks(playlist: dict) -> list[dict]:
    all_tracks = []
    cur = playlist.get("tracks", {})
    tracks = [track["track"] for track in cur.get("items", [])]

    while tracks:
        all_tracks.extend(tracks)

        next_url = cur.get("next")
        if not next_url:
            break

        print("Getting another batch of 100 tracks")
        cur = requests.get(next_url, headers=get_spotify_token_headers()).json()
        tracks = [track["track"] for track in cur.get("items", [])]

    return all_tracks


def add_playlist_tracks(conn, playlist_id: str, tracks: list[dict]):
    track_ids = [track["id"] for track in tracks]

    existing_track_ids = models.get_existing_track_ids(conn, track_ids)
    new_tracks = [track for track in tracks if track["id"] not in existing_track_ids]
    update_or_create_tracks(conn, new_tracks)

    models.insert_playlist_tracks(conn, playlist_id, track_ids)


def update_or_create_tracks(conn, all_tracks):
    all_track_ids = {track["id"] for track in all_tracks}
    all_track_data = []

    for tracks, track_ids in zip(chunked_list(all_tracks), chunked_list(all_track_ids)):
        print(f"Getting a batch of {len(track_ids)} tracks' audio features")

        tracks_features = requests.get(
            "https://api.spotify.com/v1/audio-features",
            params={"ids": ",".join(track_ids)},
            headers=get_spotify_token_headers(),
        ).json()["audio_features"]

        for track, track_features in zip(tracks, tracks_features):
            track_features = track_features or {}
            images = track.get("album", {}).get("images")
            thumbnail = images[0].get("url") if images else None

            all_track_data.append(
                (
                    track.get("id"),
                    track.get("name"),
                    thumbnail,
                    track.get("preview_url"),
                    track.get("popularity"),
                    track_features.get("danceability"),
                    track_features.get("energy"),
                    track_features.get("loudness"),
                    track_features.get("speechiness"),
                    track_features.get("acousticness"),
                    track_features.get("instrumentalness"),
                    track_features.get("liveness"),
                    track_features.get("valence"),
                    track_features.get("tempo"),
                    track_features.get("mode"),
                    track.get("duration_ms"),
                )
            )

    models.insert_or_update_tracks(conn, all_track_data)

    update_or_create_artists(conn, all_tracks)


def update_or_create_artists(conn, all_tracks):
    all_artist_ids = {
        artist["id"] for track in all_tracks for artist in track["artists"]
    }
    existing_artist_ids = models.get_existing_artist_ids(conn, list(all_artist_ids))
    new_artist_ids = [
        artist_id
        for artist_id in all_artist_ids
        if artist_id not in existing_artist_ids
    ]

    all_artist_data = []
    for artists_ids in chunked_list(new_artist_ids, 50):
        print(f"Getting a batch of {len(artists_ids)} artists")

        artists = requests.get(
            "https://api.spotify.com/v1/artists",
            params={"ids": ",".join(artists_ids)},
            headers=get_spotify_token_headers(),
        ).json()["artists"]

        for artist in artists:
            images = artist.get("images")
            thumbnail = images[0].get("url") if images else None
            all_artist_data.append(
                (
                    artist.get("id"),
                    artist.get("name"),
                    thumbnail,
                    artist.get("popularity"),
                    ",".join(artist.get("genres", [])),
                )
            )

    models.insert_or_update_artists(conn, all_artist_data)

    all_track_artists = [
        (track["id"], artist["id"])
        for track in all_tracks
        for artist in track["artists"]
    ]
    models.insert_track_artists(conn, all_track_artists)


def get_top_artists(conn, playlist_id):
    artists = models.get_playlist_artists(conn, playlist_id)
    top_artists = [
        {"name": artist.get("name"), "count": artist.get("num_tracks")}
        for artist in artists[:5]
    ]
    return top_artists, artists


def get_top_genres(artists):
    genres = [
        genre
        for artist in artists
        for genre in artist.get("genres", "").split(",")
        for _ in range(artist.get("num_tracks"))
        if genre
    ]
    top_genres = [
        {"name": genre[0], "count": genre[1]}
        for genre in sorted(Counter(genres).items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
    ]

    return top_genres, genres


@app.route("/playlist", methods=["POST"])
def sync_playlist():
    conn = get_db_connection()

    # Update playlist data
    playlist_id = request.json.get("id")
    playlist = fetch_playlist(playlist_id)
    playlist_data = update_or_create_playlist(conn, playlist)

    # Determine updated playlist track list
    all_playlist_tracks = fetch_all_playlist_tracks(playlist)
    all_playlist_track_ids = {track["id"] for track in all_playlist_tracks}
    existing_playlist_track_ids = set(models.get_playlist_track_ids(conn, playlist_id))

    # Remove old tracks from playlist
    old_playlist_track_ids = existing_playlist_track_ids.difference(
        all_playlist_track_ids
    )
    models.remove_playlist_tracks(conn, playlist_id, list(old_playlist_track_ids))

    # Add new tracks to playlist
    # Add entirely new tracks to database
    new_playlist_track_ids = all_playlist_track_ids.difference(
        existing_playlist_track_ids
    )
    new_playlist_tracks = [
        track for track in all_playlist_tracks if track["id"] in new_playlist_track_ids
    ]
    add_playlist_tracks(conn, playlist_id, new_playlist_tracks)

    # Prepping data for response
    duration = models.get_playlist_length(conn, playlist_id)
    top_artists, all_artists = get_top_artists(conn, playlist_id)
    top_genres, _ = get_top_genres(all_artists)

    conn.close()
    return (
        jsonify(
            {
                "message": "Playlist successfully synced to database",
                "data": {
                    "title": playlist_data.get("name"),
                    "description": playlist_data.get("description"),
                    "followerCount": playlist_data.get("followers_count"),
                    "trackCount": len(all_playlist_tracks),
                    "imageUrl": playlist_data.get("thumbnail"),
                    "duration": duration,
                    "topGenres": top_genres,
                    "topArtists": top_artists,
                },
                "debug": {
                    "all_track_ids": list(all_playlist_track_ids),
                    "existing_track_ids": list(existing_playlist_track_ids),
                },
            }
        ),
        200,
    )


@app.route("/reset", methods=["DELETE"])
def reset_database():
    conn = get_db_connection()
    models.reset_database(conn)
    conn.close()
    return jsonify({"message": "Database has been reset."}), 200


@app.route("/test", methods=["POST"])
def test():
    conn = get_db_connection()

    playlist_id = request.json.get("id")
    x = models.get_playlist_artists(conn, playlist_id)
    print(x)

    conn.close()
    return (
        jsonify({"message": "Database has been reset.", "data": x}),
        200,
    )


if __name__ == "__main__":
    conn = get_db_connection()
    models.create_tables(conn)
    conn.close()
    app.run(debug=True)
