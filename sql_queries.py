import psycopg2
import psycopg2.extras
from dotenv import dotenv_values
from functions import check_music_dir
import os

config = dotenv_values(".env")

# Test DB Params = dbname="blogdb", user="postgres", password=config.get("TEST_DB_PASSWORD")
# Prod DB Params = dbname="blogdb", user="andrew", password=config.get("DB_PASSWORD")


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

        return check_music_dir(user_data, song_data)

    except psycopg2.Error as error:
        print(f"An error occurred:\n{error}")
