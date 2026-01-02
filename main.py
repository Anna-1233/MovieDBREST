from fastapi import FastAPI, HTTPException, Body
import requests
import sqlite3
from typing import Any, List


tags_metadata = [
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
