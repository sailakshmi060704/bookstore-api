import sqlite3

def get_db():
    conn = sqlite3.connect("bookstore.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price INTEGER NOT NULL,
            in_stock BOOLEAN NOT NULL DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()