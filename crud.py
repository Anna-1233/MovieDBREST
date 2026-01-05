import sqlite3
from db import get_db_conn


def get_all_actors():
    db = get_db_conn()
    cursor = db.cursor()

    try:
        actors = cursor.execute('SELECT * FROM actor').fetchall()
        return actors
    finally:
        db.close()


def get_actor_by_id(actor_id: int):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        actor = cursor.execute('SELECT * FROM actor WHERE id = ?', (actor_id,)).fetchone()
        return actor
    finally:
        db.close()


def post_actor(name, surname):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check duplicates
        cursor.execute('SELECT id FROM actor WHERE name = ? AND surname = ?', (name, surname))
        existing_actor = cursor.fetchone()
        if existing_actor:
            return "duplicate"

        # insert new actor to actor table
        cursor.execute('INSERT INTO actor (name, surname) VALUES (?, ?)', (name, surname))
        new_id = cursor.lastrowid
        db.commit()
        return new_id
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def put_actor_by_id(actor_id: int, name: str, surname: str):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check if actor already exists
        cursor.execute('SELECT id FROM actor WHERE id = ?', (actor_id,))
        if not cursor.fetchone():
            return "not_found"

        # check duplicates
        cursor.execute('SELECT id FROM actor WHERE name = ? AND surname = ? AND id != ?', (name, surname, actor_id))
        existing_actor = cursor.fetchone()
        if existing_actor:
            return "duplicate"

        # update actor
        cursor.execute('UPDATE actor SET name = ?, surname = ? WHERE id = ?', (name, surname, actor_id))
        db.commit()
        return "success"
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def del_actor_by_id(actor_id: int):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check if actor already exists
        cursor.execute('SELECT id FROM actor WHERE id = ?', (actor_id,))
        if not cursor.fetchone():
            return "not_found"

        # delete actor assignments from movie_actor_through table
        cursor.execute('DELETE FROM movie_actor_through WHERE actor_id = ?', (actor_id,))

        # delete actor from actor table
        cursor.execute('DELETE FROM actor WHERE id = ?', (actor_id,))
        db.commit()

        return "success"
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def del_actors_by_ids(actor_ids: list[int]):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        ids = ', '.join(['?'] * len(actor_ids))

        # delete all actor assignments for all selected actors from movie_actor_through table
        cursor.execute(f'DELETE FROM movie_actor_through WHERE actor_id IN ({ids})', actor_ids)

        # delete all selected actors from actor table
        cursor.execute('DELETE FROM actor WHERE id IN (' + ids + ')', actor_ids)

        rows_deleted = cursor.rowcount
        db.commit()
        return rows_deleted
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_all_movies():
    db = get_db_conn()
    cursor = db.cursor()

    try:
        movies = cursor.execute('SELECT * FROM movie').fetchall()
        return movies
    finally:
        db.close()


def get_movie_by_id(movie_id: int):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        movie = cursor.execute('SELECT * FROM movie WHERE id = ?', (movie_id,)).fetchone()
        return movie
    finally:
        db.close()


def post_movie(title: str, director: str, year: int, description: str, actor_ids: list[int]):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check duplicates
        cursor.execute('SELECT id FROM movie WHERE title = ? AND year = ?', (title, year))
        existing_movie = cursor.fetchone()
        if existing_movie:
            return "duplicate"

        # insert movie into movie table
        cursor.execute('INSERT INTO movie (title, director, year, description) VALUES (?, ?, ?, ?)', (title, director, year, description))
        new_id = cursor.lastrowid

        # insert actor assignments into movie_actor_through table
        if actor_ids:
            # tuples [(movie_id, actor_id1), (movie_id, actor_id2), ...]
            unique_actor_ids = list(set(actor_ids))
            t = [(new_id, a_id) for a_id in unique_actor_ids]
            cursor.executemany('INSERT INTO movie_actor_through (movie_id, actor_id) VALUES (?, ?)', t)

        db.commit()
        return new_id
    except sqlite3.IntegrityError as e:
        db.rollback()
        return "invalid_actors"
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def put_movie_by_id(movie_id: int, title: str, director: str, year: int, description: str, actor_ids: list[int]):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check if movie already exists
        cursor.execute('SELECT id FROM movie WHERE id = ?', (movie_id,))
        if not cursor.fetchone():
            return "not_found"

        # check duplicates
        cursor.execute('SELECT id FROM movie WHERE title = ? AND year = ? AND id != ?', (title, year, movie_id))
        existing_movie = cursor.fetchone()
        if existing_movie:
            return "duplicate"

        # update movie
        cursor.execute('UPDATE movie SET title = ?, director = ?, year = ?, description = ? WHERE id = ?', (title, director, year, description, movie_id))

        # update assignments in movie_actor_through table
        if actor_ids is not None:
            cursor.execute('DELETE FROM movie_actor_through WHERE movie_id = ?', (movie_id,))

            if actor_ids:
                unique_actor_ids = list(set(actor_ids))
                t = [(movie_id, a_id) for a_id in unique_actor_ids]
                cursor.executemany('INSERT INTO movie_actor_through (movie_id, actor_id) VALUES (?, ?)', t)

        db.commit()
        return "success"
    except sqlite3.IntegrityError as e:
        db.rollback()
        return "invalid_actors"
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def del_movie_by_id(movie_id: int):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check if movie already exists
        cursor.execute('SELECT * FROM movie WHERE id = ?', (movie_id,))
        if not cursor.fetchone():
            return "not_found"

        # delete actor assignments from movie_actor_through table
        cursor.execute('DELETE FROM movie_actor_through WHERE movie_id = ?', (movie_id,))

        # delete movie from movie table
        cursor.execute('DELETE FROM movie WHERE id = ?', (movie_id,))
        db.commit()
        return "success"
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def del_movies_by_ids(movie_ids: list[int]):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        ids = ', '.join(['?'] * len(movie_ids))

        # delete all actor assignments for all selected movies
        cursor.execute(f'DELETE FROM movie_actor_through WHERE movie_id IN ({ids})', movie_ids)

        # delete all selected movies
        cursor.execute('DELETE FROM movie WHERE id IN (' + ids + ')', movie_ids)

        rows_deleted = cursor.rowcount
        db.commit()

        return rows_deleted
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_actors_for_specific_movie(movie_id: int):
    db = get_db_conn()
    cursor = db.cursor()

    try:
        # check if movie already exists
        cursor.execute('SELECT * FROM movie WHERE id = ?', (movie_id,))
        movie = cursor.fetchone()
        if not movie:
            return "not_found"

        # retrieve all actors assigned to a specific movie
        cursor.execute('SELECT a.id, a.name, a.surname FROM actor a JOIN movie_actor_through mat ON a.id = mat.actor_id WHERE mat.movie_id = ?', (movie_id,))
        actors = cursor.fetchall()
        return actors, movie
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        db.close()
