from flask import Flask, request
from database import get_db, init_db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

with app.app_context():
    init_db()

@app.route('/books')
def get_books():
    conn = get_db()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return {"books": [dict(book) for book in books]}

@app.route('/books/<int:id>')
def get_book(id):
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    conn.close()
    if book:
        return {"book": dict(book)}
    return {"error": "Book not found"}, 404

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is empty or not valid JSON"}, 400

    required_fields = ["title", "author", "price"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required field: {field}"}, 400

    if not isinstance(data["price"], (int, float)):
        return {"error": "Price must be a number"}, 400

    if not isinstance(data["title"], str) or not isinstance(data["author"], str):
        return {"error": "Title and author must be text"}, 400

    conn = get_db()
    conn.execute(
        'INSERT INTO books (title, author, price, in_stock) VALUES (?, ?, ?, ?)',
        (data["title"], data["author"], data["price"], True)
    )
    conn.commit()
    conn.close()
    return {"message": "Book added successfully"}, 201

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    if not book:
        conn.close()
        return {"error": "Book not found"}, 404
    data = request.get_json()
    updated_title = data.get("title", book["title"])
    updated_author = data.get("author", book["author"])
    updated_price = data.get("price", book["price"])
    updated_in_stock = data.get("in_stock", book["in_stock"])
    conn.execute(
        'UPDATE books SET title = ?, author = ?, price = ?, in_stock = ? WHERE id = ?',
        (updated_title, updated_author, updated_price, updated_in_stock, id)
    )
    conn.commit()
    conn.close()
    return {"message": "Book updated successfully"}

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    if not book:
        conn.close()
        return {"error": "Book not found"}, 404
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return {"message": f"Book with id {id} has been deleted"}

if __name__ == '__main__':
    app.run(debug=True)