# Bookstore API

A RESTful API built with Python, Flask, and SQLite.

## Features
- Get all books
- Get a single book by ID
- Add a new book
- Update a book
- Delete a book
- Input validation and error handling
- Frontend UI built with HTML, CSS and JavaScript

## Technologies Used
- Python
- Flask
- SQLite
- HTML, CSS, JavaScript

## How to Run
1. Install dependencies: `pip install flask flask-cors`
2. Run the server: `python app.py`
3. Open `index.html` in your browser
4. API runs at: `http://127.0.0.1:5000`

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /books | Get all books |
| GET | /books/<id> | Get a single book |
| POST | /books | Add a new book |
| PUT | /books/<id> | Update a book |
| DELETE | /books/<id> | Delete a book |
