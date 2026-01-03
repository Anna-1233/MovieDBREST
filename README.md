
# 🎥 MoviesDBREST Project (FastAPI)

## Description
A RESTful API for managing a movie database, built with FastAPI and SQLite.

## Endpoints

| Method | Endpoint                      | Description                                                            |
|--------|-------------------------------|------------------------------------------------------------------------|
| GET    | ```/actors```                 | Retrieve a list of all actors from the database.                       |
| GET    | ```/actor/{actor_id}```       | Retrieve detailed information about an actor by his unique ID.         |
| POST   | ```/actors```                 | Add an actor to the database.                                          |
| PUT    | ```/actors/{actor_id}```      | Edit and update existing an actor from the database.                   |
| DELETE | ```/actors/{actor_id}```      | Delete an actor and his associations from database.                    |
| DELETE | ```/actors/batch```           | Delete multiple actors and their associations by their IDs.            |
| GET    | ```/movies```                 | Retrieve a list of all movies from the database.                       |
| GET    | ```/movies/{movie_id}```      | Retrieve detailed information about a specific movie by its unique ID. |
| GET    | ```/movies/{movies}/actors``` | Retrieve actors information for specific movie.                        |
| POST   | ```/movies```                 | Add a new movie actor assignments to the database.                     |
| PUT    | ```/movies/{movie_id}```      | Edit and update existing movie from the database.                      |
| DELETE | ```/movies/{movie_id}```      | Delete a movie and his associations from the database.                 |
| DELETE | ```/movies/batch```           | Delete multiple movies and their associations by their IDs.            |


## Technologies used

| Tool / Library              | Description                                             |
|-----------------------------|---------------------------------------------------------|
| **Python 3.13+**            | Programming language - backend.                         |
| **FastAPI**                 | web framework for building the API.                     |
| **SQLite**                  | Relational database for data storage.                   |
| **Uvicorn (ASGI Server)**   | The high-performance web server to run the application. |

## Project structure
```
MoviesDBREST/ 
├── main.py
├── test_main.http
├── movies-extended.db
├── requirements.txt
├── README.md
└── .gitignore
```

## Demo database
<p style="text-align: justify;">

The project includes a demonstration SQLite database ```movies-extended.db``` with sample data
to allow quick startup and testing of the API.
The database is intended for development purposes only.
</p>

## Installation
1. Clone the repository:
```
git https://github.com/Anna-1233/MovieDBREST.git

cd MovieDBREST
```
2. Create and activate virtual environment:
```
python -m venv venv

source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Running
1. Start the server:
```
uvicorn main:app --reload
```
2. Access the API in browser using http://127.0.0.1:8000.


3. Open API documentation: Go to http://127.0.0.1:8000/docs to see the interactive Swagger UI.


4. Stop the server with ```Ctrl + C```.

## Testing
1. Testing directly in Swagger UI:<br>
Go to http://127.0.0.1:8000/docs.
Each endpoint includes ```Try it out``` button that allows to send requests directly from the browser, inspect request/response bodies, and verify that the API behaves as expected.


2. Testing using ```test_main.http``` file:<br>
The project includes ```test_main.http``` file that allows to test API endpoints directly from editor (e.g., VS Code, PyCharm).
Each request in the file represents a specific API call (GET, POST, PUT, DELETE) and can be
run directly from the editor using the built‑in HTTP client.


3. Testing using ```curl``` in the terminal:<br>
In examples below replace the method, URL, headers, and body depending on the endpoint you want to test.

- Ex 1:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/movies/1' \
  -H 'accept: application/json'
```

- Ex 2:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/movies' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '  {
    "title": "Pulp Fiction",
    "year": 1994,
    "actors": "Tim Roth, Amanda Plummer, Laura Lovelace, John Travolta"
  }'
```
- Ex 3:
```
curl -X 'DELETE' \
  'http://127.0.0.1:8000/movies/10' \
  -H 'accept: application/json'
```

## Author
**Anna Czopko** \
📧 aczopko@student.agh.edu.pl