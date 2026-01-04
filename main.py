from fastapi import FastAPI, HTTPException, Body
import requests
from typing import Any, List
import crud

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
        "description": "Other endpoints - not related to MovieDBREST.",
    },
]


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
def get_actors():
    """
    Retrieve a list of all actors from the database.
    """
    rows = crud.get_all_actors()
    return [dict(row) for row in rows]


@app.get('/actors/{actor_id}', tags=["Actors"])
def get_single_actor(actor_id:int):
    """
    Retrieve detailed information about an actor by his unique ID.
    Returns 404 if an actor is not found.
    """
    row = crud.get_actor_by_id(actor_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Actor not found!")
    return dict(row)


@app.post('/actors', tags=["Actors"])
def add_actor(params: dict[str, Any]):
    """
    Add an actor to the database.
    Checks for duplicates before inserting. Returns the ID of the newly added actor.
    """
    name = params.get("name")
    surname = params.get("surname")

    if not name or not surname:
        raise HTTPException(status_code=400, detail="All fields: name and surname are required!")

    try:
        result = crud.post_actor(name, surname)

        if result == "duplicate":
            raise HTTPException(status_code=409, detail="Actor already exists!")
        return {"message": "Actor has been added successfully!", "id": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put('/actors/{actor_id}', tags=["Actors"])
def edit_actor(actor_id: int, params: dict[str, Any]):
    """
    Edit and update an actor from the database.
    Checks for duplicates before updating.
    Returns 404 if actor is not found.
    """
    new_name = params.get("name")
    new_surname = params.get("surname")

    if not new_name or not new_surname:
        raise HTTPException(status_code=400, detail="All fields: name and surname are required!")

    try:
        result = crud.put_actor_by_id(actor_id, new_name, new_surname)

        if result == "duplicate":
            raise HTTPException(status_code=409, detail="Actor already exists! Update not allowed!")
        elif result == "not_found":
            raise HTTPException(status_code=404, detail="Actor not found!")
        return {"message": f"Actor {actor_id} updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/actors/batch', tags=["Actors"])
def del_actors(actor_ids: List[int] = Body(...)):
    """
    Delete multiple actors by their IDs.
    Example: [5, 6, 10]
    """
    if not actor_ids:
        raise HTTPException(status_code=400, detail="No actor(s) to remove! Please select at least one actor.")

    try:
        rows_deleted = crud.del_actors_by_ids(actor_ids)

        if rows_deleted < len(actor_ids):
            return {
                "message": f"Operation partially successful. Deleted {rows_deleted} out of {len(actor_ids)} requested actors.",
                "requested_ids": actor_ids,
                "deleted_count": rows_deleted
            }
        return {"message": f"All selected actors with their associations deleted successfully!", "deleted_ids": actor_ids, "deleted_count": rows_deleted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/actors/{actor_id}', tags=["Actors"])
def del_actor(actor_id: int):
    """
    Delete an actor from the database.
    Returns 404 if actor is not found.
    """
    try:
        result = crud.del_actor_by_id(actor_id)
        if result == "not_found":
            raise HTTPException(status_code=404, detail="Actor not found!")
        return {"message": f"Actor with id {actor_id} deleted successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------- Movies Endpoints --------
@app.get('/movies', tags=["Movies"])
def get_movies():
    """
    Retrieve a list of all movies from the database.
    """
    rows = crud.get_all_movies()
    return [dict(row) for row in rows]


@app.get('/movies/{movie_id}', tags=["Movies"])
def get_single_movie(movie_id:int):
    """
    Retrieve detailed information about a specific movie by its unique ID.
    Returns 404 if the movie is not found.
    """
    row = crud.get_movie_by_id(movie_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Movie not found!")
    return dict(row)


@app.post('/movies', tags=["Movies"])
def add_movie(params: dict[str, Any]):
    """
    Add a new movie to the database.
    Checks for duplicates before inserting. Returns the ID of the newly created movie.
    """
    title = params.get("title")
    director = params.get("director")
    year = params.get("year")
    description = params.get("description")
    actor_ids = params.get("actor_ids", [])

    if not title or not year or not director:
        raise HTTPException(status_code=400, detail="Fields title/director/year are required!")

    try:
        result = crud.post_movie(title, director, year, description, actor_ids)

        if result == "duplicate":
            raise HTTPException(status_code=409, detail="Movie already exists! Update not allowed!")
        elif result == "invalid_actors":
            raise HTTPException(status_code=400, detail="One or more actor IDs do not exist.")
        return {"message": "Movie added successfully!",
                "movie_id": result,
                "added_actor_count": len(set(actor_ids))
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put('/movies/{movie_id}', tags=["Movies"])
def edit_movie(movie_id: int, params: dict[str, Any]):
    """
    Update movie details and refresh actor assignments.
    Checks for duplicates before updating.
    Returns 404 if the movie is not found.
    """
    new_title = params.get("title")
    new_director = params.get("director")
    new_year = params.get("year")
    new_description = params.get("description")
    new_actor_ids = params.get("actor_ids")

    if not new_title or not new_year or not new_director:
        raise HTTPException(status_code=400, detail="Fields title/director/year are required!")

    try:
        result = crud.put_movie_by_id(movie_id, new_title, new_director, new_year, new_description, new_actor_ids)
        if result == "duplicate":
            raise HTTPException(status_code=409, detail="Movie already exists! Update not allowed!")
        elif result == "invalid_actors":
            raise HTTPException(status_code=400, detail="One or more actor IDs do not exist.")
        return {
            "message": f"Movie {movie_id} and actors updated successfully!",
            "id": movie_id,
            "updated_actors_count": len(set(new_actor_ids or []))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/movies/batch', tags=["Movies"])
def del_movies(movie_ids: List[int] = Body(...)):
    """
    Delete multiple movies by their IDs.
    Example: [5, 6, 10]
    """
    if not movie_ids:
        raise HTTPException(status_code=400, detail="No movie(s) to remove! Please select at least one movie.")

    try:
        rows_deleted = crud.del_movies_by_ids(movie_ids)

        if rows_deleted < len(movie_ids):
            return {
                "message": f"Operation partially successful. Deleted {rows_deleted} out of {len(movie_ids)} requested movies.",
                "requested_ids": movie_ids,
                "actual_deleted_count": rows_deleted
            }
        return {"message": f"All selected movies with their associations deleted successfully!", "deleted_ids": movie_ids}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/movies/{movie_id}', tags=["Movies"])
def del_movie(movie_id: int):
    """
    Delete a movie from the database.
    Returns 404 if the movie is not found.
    """
    try:
        result = crud.del_movie_by_id(movie_id)
        if result == "not_found":
            raise HTTPException(status_code=404, detail="Movie not found!")
        return {"message": f"Movie with id {movie_id} deleted successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/movies/{movie_id}/actors', tags=["Movies"])
def get_actors_for_movie(movie_id: int):
    """
    Retrieve all actors assigned to a specific movie.
    """
    try:
        result = crud.get_actors_for_specific_movie(movie_id)
        if result == "not_found":
            raise HTTPException(status_code=404, detail="Movie not found!")

        actors, movie = result
        return {
            "movie_title": movie["title"],
            "actors": [dict(row) for row in actors]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
