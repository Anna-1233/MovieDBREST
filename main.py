from fastapi import FastAPI, HTTPException, Body
import requests
import sqlite3
from typing import Any, List


tags_metadata = [
    {
        "name": "Actors",
        "description": "Management of the actors catalog.",
    },
    {
        "name": "Movies",
        "description": "Management of the movie catalog.",
    },
    {
        "name": "Other",
        "description": "Other endpoints - not related to Movies.",
    },
]


# app = FastAPI(openapi_tags=tags_metadata, swagger_ui_parameters={"operationsSorter": "alpha"})

app = FastAPI(
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"operationsSorter": "alpha"}
)

@app.get("/", tags=["Other"])
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", tags=["Other"])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/sum", tags=["Other"])
def sum(x: int = 0, y: int = 10):
    return x+y


@app.get("/geocode", tags=["Other"])
def sum(lat: float, lon: float):
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    # http://127.0.0.1:8000/geocode?lat=50.0680275&lon=19.9098668
    return response.json()


# ---------------------------------
# ---------- MovieDBREST ----------
# ---------------------------------

# ------- Actors Endpoints --------

@app.get('/actors', tags=["Actors"])
def actors():
    """
    Retrieve a list of all actors from the database.
    """
    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()
    actors = cursor.execute('SELECT * FROM actor').fetchall()
    output = []
    for actor in actors:
        actor = {'id': actor[0], 'name': actor[1], 'surname': actor[2]}
        output.append(actor)
    return output


@app.get('/actors/{actor_id}', tags=["Actors"])
def get_single_actor(actor_id:int):
    """
    Retrieve detailed information about an actor by his unique ID.
    Returns 404 if an actor is not found.
    """
    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()
    actor = cursor.execute(f"SELECT * FROM actor WHERE id={actor_id}").fetchone()
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found!")
    return {'id': actor[0], 'name': actor[1], 'surname': actor[2]}


@app.post('/actors', tags=["Actors"])
def add_actor(params: dict[str, Any]):
    """
    Add an actor to the database.
    Checks for duplicates before inserting. Returns the ID of the newly added actor.
    """
    name = params.get("name")
    surname = params.get("surname")

    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()

    if not name or not surname:
        raise HTTPException(status_code=400, detail="All fields: name and surname are required!")

    # check duplicates
    cursor.execute('SELECT id FROM actor WHERE name = ? AND surname = ?', (name, surname))
    existing_actor = cursor.fetchone()
    if existing_actor:
        db.close()
        raise HTTPException(status_code=409, detail="Actor already exists in database!")

    cursor.execute('INSERT INTO actor (name, surname) VALUES (?, ?)', (name, surname))
    db.commit()
    new_id = cursor.lastrowid
    db.close()

    return {"message": "Actor has been added successfully!", "id": new_id}


@app.put('/actors/{actor_id}', tags=["Actors"])
def edit_actor(actor_id: int, params: dict[str, Any]):
    """
    Edit and update an actor from the database.
    Checks for duplicates before updating.
    Returns 404 if actor is not found.
    """
    new_name = params.get("name")
    new_surname = params.get("surname")

    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()

    # check duplicates
    cursor.execute('SELECT id FROM actor WHERE name = ? AND surname = ? AND id != ?', (new_name, new_surname, actor_id))
    existing_actor = cursor.fetchone()
    if existing_actor:
        db.close()
        raise HTTPException(status_code=409, detail="Actor already exists. Update not allowed!")

    cursor.execute('UPDATE actor SET name = ?, surname = ? WHERE id = ?',
                   (new_name, new_surname, actor_id))
    db.commit()

    rows_affected = cursor.rowcount
    db.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Actor not found!")

    return {"message": f"Actor {actor_id} updated successfully!"}


@app.delete('/actors/batch', tags=["Actors"])
def del_actors(actor_ids: List[int] = Body(...)):
    """
    Delete multiple actors by their IDs.
    Example: [5, 6, 10]
    """
    if not actor_ids:
        raise HTTPException(status_code=400, detail="No actor(s) to remove! Please select at least one actor.")

    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()

    ids = ', '.join(['?'] * len(actor_ids))
    cursor.execute('DELETE FROM actor WHERE id IN (' + ids + ')', actor_ids)
    db.commit()

    rows_deleted = cursor.rowcount
    db.close()

    if rows_deleted < len(actor_ids):
        return {
            "message": f"Operation partially successful. Deleted {rows_deleted} out of {len(actor_ids)} requested movies.",
            "requested_ids": actor_ids,
            "actual_deleted_count": rows_deleted
        }

    return {"message": f"All selected actors deleted successfully!", "deleted_ids": actor_ids}


@app.delete('/actors/{actor_id}', tags=["Actors"])
def del_actor(actor_id: int):
    """
    Delete an actor from the database.
    Returns 404 if actor is not found.
    """
    db = sqlite3.connect('movies-extended.db')
    cursor = db.cursor()

    cursor.execute('DELETE FROM actor WHERE id = ?', (actor_id,))
    db.commit()

    rows_affected = cursor.rowcount
    db.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Actor not found!")

    return {"message": f"Actor with id {actor_id} deleted successfully!"}


# ------- Movies Endpoints --------
@app.get('/movies', tags=["Movies"])
def get_movies():
    """
    Retrieve a list of all movies from the database.
    """
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    movies = cursor.execute('SELECT * FROM movies').fetchall()
    output = []
    for movie in movies:
        movie = {'id': movie[0], 'title': movie[1], 'year': movie[2], 'actors': movie[3]}
        output.append(movie)
    return output


@app.get('/movies/{movie_id}', tags=["Movies"])
def get_single_movie(movie_id:int):
    """
    Retrieve detailed information about a specific movie by its unique ID.
    Returns 404 if the movie is not found.
    """
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    movie = cursor.execute(f"SELECT * FROM movies WHERE id={movie_id}").fetchone()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found!")
    return {'id': movie[0], 'title': movie[1], 'year': movie[2], 'actors': movie[3]}


@app.post('/movies', tags=["Movies"])
def add_movie(params: dict[str, Any]):
    """
    Add a new movie to the database.
    Checks for duplicates before inserting. Returns the ID of the newly created movie.
    """
    title = params.get("title")
    year = params.get("year")
    actors = params.get("actors")

    db = sqlite3.connect('movies.db')
    cursor = db.cursor()

    if not title or not year or not actors:
        raise HTTPException(status_code=400, detail="All fields title/year/actors are required!")

    # check duplicates
    cursor.execute('SELECT id FROM movies WHERE title = ? AND year = ?', (title, year))
    existing_movie = cursor.fetchone()
    if existing_movie:
        db.close()
        raise HTTPException(status_code=409, detail="Movie already exists!")

    cursor.execute('INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)', (title, year, actors))
    db.commit()
    new_id = cursor.lastrowid
    db.close()

    return {"message": "Movie has been added successfully!", "id": new_id}


@app.delete('/movies/batch', tags=["Movies"])
def del_movies(movie_ids: List[int] = Body(...)):
    """
    Delete multiple movies by their IDs.
    Example: [5, 6, 10]
    """
    if not movie_ids:
        raise HTTPException(status_code=400, detail="No movie(s) to remove! Please select at least one movie.")

    db = sqlite3.connect('movies.db')
    cursor = db.cursor()

    ids = ', '.join(['?'] * len(movie_ids))
    cursor.execute('DELETE FROM movies WHERE id IN (' + ids + ')', movie_ids)
    db.commit()

    rows_deleted = cursor.rowcount
    db.close()

    if rows_deleted < len(movie_ids):
        return {
            "message": f"Operation partially successful. Deleted {rows_deleted} out of {len(movie_ids)} requested movies.",
            "requested_ids": movie_ids,
            "actual_deleted_count": rows_deleted
        }

    return {"message": f"All selected movies deleted successfully!", "deleted_ids": movie_ids}



@app.delete('/movies/{movie_id}', tags=["Movies"])
def del_movie(movie_id: int):
    """
    Delete a movie from the database.
    Returns 404 if the movie is not found.
    """
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()

    cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
    db.commit()

    rows_affected = cursor.rowcount
    db.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Movie not found!")

    return {"message": f"Movie with id {movie_id} deleted successfully!"}


@app.put('/movies/{movie_id}', tags=["Movies"])
def edit_movie(movie_id: int, params: dict[str, Any]):
    """
    Edit and update a movie from the database.
    Checks for duplicates before updating.
    Returns 404 if the movie is not found.
    """
    new_title = params.get("title")
    new_year = params.get("year")
    new_actors = params.get("actors")

    db = sqlite3.connect('movies.db')
    cursor = db.cursor()

    # check duplicates
    cursor.execute('SELECT id FROM movies WHERE title = ? AND year = ? AND id != ?', (new_title, new_year, movie_id))
    existing_movie = cursor.fetchone()
    if existing_movie:
        db.close()
        raise HTTPException(status_code=409, detail="Movie already exists. Update not allowed!")

    cursor.execute('UPDATE movies SET title = ?, year = ?, actors = ? WHERE id = ?', (new_title, new_year, new_actors, movie_id))
    db.commit()

    rows_affected = cursor.rowcount
    db.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Movie not found!")

    return {"message": f"Movie {movie_id} updated successfully!"}
