from flask import Flask, request, jsonify, send_from_directory
from database import get_db, init_db
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'bookstore-secret-key'
jwt = JWTManager(app)

with app.app_context():
    init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is empty or not valid JSON"}, 400

    if not data.get("username") or not data.get("password"):
        return {"error": "Username and password are required"}, 400

    hashed_password = generate_password_hash(data["password"])

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (data["username"], hashed_password)
        )
        conn.commit()
        return {"message": "User registered successfully"}, 201
    except:
        return {"error": "Username already exists"}, 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is empty or not valid JSON"}, 400

    if not data.get("username") or not data.get("password"):
        return {"error": "Username and password are required"}, 400

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (data["username"],)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], data["password"]):
        return {"error": "Invalid username or password"}, 401

    access_token = create_access_token(identity=data["username"])
    return {"access_token": access_token}, 200

@app.route('/books')
def get_books():
    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = (page - 1) * limit

    # Filtering parameters
    author = request.args.get("author", None)
    min_price = request.args.get("min_price", None, type=int)
    max_price = request.args.get("max_price", None, type=int)
    in_stock = request.args.get("in_stock", None)

    # Build query dynamically
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if author:
        query += " AND author LIKE ?"
        params.append(f"%{author}%")

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    if in_stock is not None:
        query += " AND in_stock = ?"
        params.append(1 if in_stock.lower() == "true" else 0)

    # Get total count for pagination info
    conn = get_db()
    total = conn.execute(
        query.replace("SELECT *", "SELECT COUNT(*)"), params
    ).fetchone()[0]

    # Apply pagination
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    books = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "books": [dict(book) for book in books]
    }

@app.route('/books/<int:id>')
def get_book(id):
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    conn.close()
    if book:
        return {"book": dict(book)}
    return {"error": "Book not found"}, 404

@app.route('/books', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
    app.run(debug=False)