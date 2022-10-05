import psycopg2
import psycopg2.extras
from dotenv import dotenv_values
from functions import check_music_dir, upload_tab_file

config = dotenv_values(".env")

# Test DB Params = dbname="blogdb", user="postgres", password=config.get("TEST_DB_PASSWORD")
# Prod DB Params = dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")


def query_users():
    """ Fetches all users in the db"""
    conn = None
    try:
        with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_query = """
                    SELECT * FROM users
                    ORDER BY id ASC;
                """
                cur.execute(user_query)
                data = cur.fetchall()
                cur.close()
                return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()


def get_user_songs(user_id):
    """ This will fetch all the user's songs and return them as tuples """

    conn = None

    try:
        conn = psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD"))
        cur = conn.cursor()
        query = f"""
            SELECT
                songs.id,
                artist,
                album,
                song_name,
                song_file
            FROM
                songs
            INNER JOIN artists
                ON artists.id = songs.artist_id
            INNER JOIN albums
                ON albums.id = songs.album_id
            WHERE user_id = { user_id }
            ORDER BY albums;
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()


def delete_song(user_id, song_id):
    """ Deletes a specific song from the db
    and server; if there aren't any songs left
    in the server, the album folder will be deleted
    as well as the album from the db """

    try:
        with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                song_query = f"""
                    SELECT 
                        s.id id,
                        art.artist,
                        alb.id as album_id,
                        alb.album,
                        s.song_name,
                        s.song_file
                    FROM songs s
                    INNER JOIN artists art
                        ON art.id = s.artist_id
                    INNER JOIN albums alb
                        ON  alb.id = s.album_id
                    WHERE
                        s.id = {song_id}
                """
                cur.execute(song_query)
                song_data = cur.fetchone()

        with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                user_query = f"""
                    SELECT
                        id,
                        name
                    FROM users u
                    WHERE
                        u.id = {user_id}
                """
                cur.execute(user_query)
                user_data = cur.fetchone()

        with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                delete_query = f"""
                    DELETE FROM
                        songs
                    WHERE songs.id = {song_id}
                """
                cur.execute(delete_query)

        check_dir = check_music_dir(user_data, song_data)

        if check_dir[2] == 1:
            with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    album_dir_delete_query = f"""
                        DELETE FROM
                            albums
                        WHERE albums.id = {song_data["album_id"]}
                    """
                    cur.execute(album_dir_delete_query)

        return check_dir

    except psycopg2.Error as error:
        print(f"An error occurred:\n{error}")


def get_all_artists_audio():
    """ Queries all audio artists in the DB """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = """
                SELECT
                    id,
                    artist
                FROM artists
            """
            cur.execute(query)
            res = cur.fetchall()
            all_artists = {row["id"]: row["artist"] for row in res}
            return all_artists


def get_all_albums_audio(artist_id):
    """ Queries all audio albums from a specific artist """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = f"""
                SELECT
                    id,
                    album
                FROM albums
                WHERE artist_id = {artist_id}
                ORDER BY album
            """
            cur.execute(query)
            res = cur.fetchall()
            albums = [{"id": row["id"], "album": row["album"]} for row in res]
            return albums


def get_album_songs(album_id):
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = f"""
                SELECT
                    ref_id,
                    song_name
                FROM songs
                INNER JOIN albums
                    ON albums.id = album_id
                WHERE album_id = {album_id}
                ORDER BY track_number ASC
            """
            cur.execute(query)
            res = cur.fetchall()
            all_songs = {song["ref_id"]: {"song_name": song["song_name"]} for song in res}
            return all_songs


def get_all_songs_audio(artist):
    """ Queries all audio songs from the database """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = f"""
                SELECT 
                    s.song_name,
                    s.ref_id
                FROM songs s
                INNER JOIN artists ar
                    ON ar.id = s.artist_id
                INNER JOIN albums al
                    ON al.id = s.album_id
                WHERE ar.artist = '{artist}'
                ORDER BY al.album ASC
            """
            cur.execute(query)
            all_songs = cur.fetchall()
            songs_dict = {
                song["ref_id"]: {
                    "song_name": song["song_name"]
                }
                for song in all_songs}
            return songs_dict


def get_song_audio(_id):
    """ Gets a specific song based on the reference id """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = f"""
                SELECT
                    s.ref_id,
                    ar.artist,
                    al.album,
                    s.song_name,
                    s.album_art,
                    s.song_file
                FROM songs s
                INNER JOIN artists ar
                    ON ar.id = s.artist_id
                INNER JOIN albums al
                    ON al.id = s.album_id
                WHERE s.ref_id = '{_id}'
            """
            cur.execute(query)
            song_data = cur.fetchall()
            song_dict = {
                song["ref_id"]:
                    {
                        "artist": song["artist"],
                        "album": song["album"],
                        "song_name": song["song_name"],
                        "album_art": song["album_art"],
                        "song_file": song["song_file"]
                    }
                for song in song_data}
            return song_dict

# ######## All queries related to guitar-tabs ########


def get_all_artists_tabs():
    """
        Queries the song_tabs table and pulls all the data and stores it into a dictionary
    """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            tab_query = f"""
                SELECT DISTINCT artist FROM song_tabs
            """
            cur.execute(tab_query)
            all_tabs = cur.fetchall()

    artist_list = [row['artist'] for row in all_tabs]

    return artist_list


def get_all_song_tabs(artist):
    """
    Pulls all tabs related to the artist requested
    :return:
    """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = f"""
                SELECT *
                FROM song_tabs
                WHERE artist = '{artist}';
            """
            cur.execute(query)
            songs = cur.fetchall()

            songs_dict = {song["tab_name"]: {"file": song["tab_file"], "album": song["album"]} for song in songs}
            return songs_dict


def upload_tab(form_data):
    """
    Uploads the tablature file into the server and adds it the db.
    """
    can_upload = upload_tab_file(form_data)
    if can_upload[0]:
        with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
            with conn.cursor() as cur:
                upload_query = f"""
                    INSERT INTO song_tabs
                        (artist, tab_name, tab_file, album)
                    VALUES
                        ('{form_data['artist']}', '{form_data['tab_name']}', '{can_upload[1]}', '{form_data['album']}');
                """
                cur.execute(upload_query)
                return True
    else:
        return False


def get_song(artist, song_name):
    """
    Gets the songFile based on the song and artist name
    :param artist:
    :param song_name:
    :return:
    query of the song path
    """
    with psycopg2.connect(dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")) as conn:
        with conn.cursor() as cur:
            query = f"""
                SELECT tab_file
                FROM song_tabs
                WHERE artist = '{artist}'
                AND tab_name = '{song_name}'
            """
            cur.execute(query)
            song_file = cur.fetchone()
            return song_file[0]