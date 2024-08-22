from psycopg2.extras import DictCursor, RealDictCursor, execute_values

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS artists (
    id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(80),
    thumbnail VARCHAR(300),
    popularity INTEGER,
    genres VARCHAR(300)
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

CREATE TABLE IF NOT EXISTS track_artists (
    track_id VARCHAR(80) REFERENCES tracks(id),
    artist_id VARCHAR(80) REFERENCES artists(id),
    PRIMARY KEY (track_id, artist_id)
);

CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id VARCHAR(80) REFERENCES playlists(id),
    track_id VARCHAR(80) REFERENCES tracks(id),
    PRIMARY KEY (playlist_id, track_id)
);
"""

DROP_TABLES = """
DROP TABLE track_artists;
DROP TABLE playlist_tracks;
DROP TABLE playlists CASCADE;
DROP TABLE artists CASCADE;
DROP TABLE tracks CASCADE;
"""


def create_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLES)
    conn.commit()


def reset_database(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(DROP_TABLES)
        cur.execute(CREATE_TABLES)
    conn.commit()


def remove_playlist_tracks(conn, playlist_id: str, track_ids: list[str]) -> None:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            DELETE FROM playlist_tracks
            WHERE playlist_id = %s
            AND track_id = ANY(%s)
        """,
            (playlist_id, track_ids),
        )
    conn.commit()


def insert_playlist_tracks(conn, playlist_id: str, track_ids: list[str]) -> None:
    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO playlist_tracks (playlist_id, track_id)
        VALUES %s
        """
        data = [(playlist_id, track_id) for track_id in track_ids]
        execute_values(cur, insert_query, data)
    conn.commit()


def insert_track_artists(conn, track_artist_data: list[tuple[str, str]]) -> None:
    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO track_artists (track_id, artist_id)
        VALUES %s
        """
        execute_values(cur, insert_query, track_artist_data)
    conn.commit()


def insert_or_update_tracks(conn, tracks_data: list[tuple]) -> None:
    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO tracks (id, name, thumbnail, preview_url, popularity, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, mode, duration_ms)
        VALUES %s
        """
        execute_values(cur, insert_query, tracks_data)
    conn.commit()


def insert_or_update_artists(conn, artists_data: list[tuple]) -> None:
    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO artists (id, name, thumbnail, popularity, genres)
        VALUES %s
        """
        execute_values(cur, insert_query, artists_data)
    conn.commit()


def insert_or_update_playlist(conn, playlist: dict) -> None:
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


def get_existing_track_ids(conn, track_ids: list[str]) -> list[str]:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            SELECT id
            FROM tracks
            WHERE id = ANY(%s)
        """,
            (track_ids,),
        )
        return [row[0] for row in cur.fetchall()]


def get_existing_artist_ids(conn, artist_ids: list[str]) -> list[str]:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            SELECT id
            FROM artists
            WHERE id = ANY(%s)
        """,
            (artist_ids,),
        )
        return [row[0] for row in cur.fetchall()]


def get_playlist_length(conn, playlist_id: str) -> tuple[int, int]:
    """Returns playlist length in seconds"""
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            SELECT SUM(duration_ms) / 1000.0
            FROM (
                SELECT duration_ms
                FROM tracks
                WHERE id = ANY(
                    SELECT track_id
                    FROM playlist_tracks
                    WHERE playlist_id = %s
                )
            )
        """,
            (playlist_id,),
        )
        return float(cur.fetchone()[0])


def get_playlist_artists(conn, playlist_id: str) -> list[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT artists.name, artists.genres, artists.thumbnail, artists.popularity, COUNT(tracks.id) as num_tracks
            FROM tracks
            JOIN track_artists
            ON track_id = tracks.id
            JOIN artists
            ON artist_id = artists.id
            WHERE tracks.id IN (
                SELECT track_id
                FROM playlist_tracks
                WHERE playlist_id = %s
            )
            GROUP BY artists.name, artists.genres, artists.thumbnail, artists.popularity
            ORDER BY num_tracks DESC;
        """,
            (playlist_id,),
        )
        return cur.fetchall()


def get_playlist_track_ids(conn, playlist_id: str) -> list[str]:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            """
            SELECT track_id 
            FROM playlist_tracks 
            WHERE playlist_id = %s
        """,
            (playlist_id,),
        )
        return [row[0] for row in cur.fetchall()]
