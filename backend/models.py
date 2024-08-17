from psycopg2.extras import RealDictCursor

# SQL statements for table creation
CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS artists (
    id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(80),
    thumbnail VARCHAR(300),
    popularity INTEGER
);

CREATE TABLE IF NOT EXISTS tracks (
    id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(80),
    thumbnail VARCHAR(300),
    preview_url VARCHAR(300),
    popularity INTEGER,
    danceability FLOAT,
    energy FLOAT,
    loudness FLOAT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    mode INTEGER,
    duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS playlists (
    id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(80),
    description TEXT,
    thumbnail VARCHAR(300),
    followers_count INTEGER
);

CREATE TABLE IF NOT EXISTS artists_tracks (
    artist_id VARCHAR(80) REFERENCES artists(id),
    track_id VARCHAR(80) REFERENCES tracks(id),
    PRIMARY KEY (artist_id, track_id)
);

CREATE TABLE IF NOT EXISTS playlists_tracks (
    playlist_id VARCHAR(80) REFERENCES playlists(id),
    track_id VARCHAR(80) REFERENCES tracks(id),
    PRIMARY KEY (playlist_id, track_id)
);

CREATE TABLE IF NOT EXISTS artists_genres (
    artist_id VARCHAR(80) REFERENCES artists(id),
    genre VARCHAR(80),
    PRIMARY KEY (artist_id, genre)
);
"""


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLES)
    conn.commit()


def insert_or_update_artist(conn, artist):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO artists (id, name, thumbnail, popularity)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                thumbnail = EXCLUDED.thumbnail,
                popularity = EXCLUDED.popularity
        """,
            (artist["id"], artist["name"], artist["thumbnail"], artist["popularity"]),
        )
    conn.commit()


def insert_or_update_track(conn, track):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tracks (id, name, thumbnail, preview_url, popularity, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, mode, duration_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                thumbnail = EXCLUDED.thumbnail,
                preview_url = EXCLUDED.preview_url,
                popularity = EXCLUDED.popularity,
                danceability = EXCLUDED.danceability,
                energy = EXCLUDED.energy,
                loudness = EXCLUDED.loudness,
                speechiness = EXCLUDED.speechiness,
                acousticness = EXCLUDED.acousticness,
                instrumentalness = EXCLUDED.instrumentalness,
                liveness = EXCLUDED.liveness,
                valence = EXCLUDED.valence,
                tempo = EXCLUDED.tempo,
                mode = EXCLUDED.mode,
                duration_ms = EXCLUDED.duration_ms
        """,
            (
                track["id"],
                track["name"],
                track["thumbnail"],
                track["preview_url"],
                track["popularity"],
                track["danceability"],
                track["energy"],
                track["loudness"],
                track["speechiness"],
                track["acousticness"],
                track["instrumentalness"],
                track["liveness"],
                track["valence"],
                track["tempo"],
                track["mode"],
                track["duration_ms"],
            ),
        )
    conn.commit()


def insert_or_update_playlist(conn, playlist):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO playlists (id, name, description, thumbnail, followers_count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                description = EXCLUDED.description,
                thumbnail = EXCLUDED.thumbnail,
                followers_count = EXCLUDED.followers_count
        """,
            (
                playlist["id"],
                playlist["name"],
                playlist["description"],
                playlist["thumbnail"],
                playlist["followers_count"],
            ),
        )
    conn.commit()


def insert_artist_track(conn, artist_id, track_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO artists_tracks (artist_id, track_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """,
            (artist_id, track_id),
        )
    conn.commit()


def insert_playlist_track(conn, playlist_id, track_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO playlists_tracks (playlist_id, track_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """,
            (playlist_id, track_id),
        )
    conn.commit()


def insert_artist_genre(conn, artist_id, genre):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO artists_genres (artist_id, genre)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """,
            (artist_id, genre),
        )
    conn.commit()


def get_all_playlists(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM playlists")
        return cur.fetchall()


def get_all_tracks(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM tracks")
        return cur.fetchall()


def get_all_artists(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM artists")
        return cur.fetchall()
