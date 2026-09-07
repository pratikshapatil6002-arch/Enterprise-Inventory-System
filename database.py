import sqlite3
from config import DATABASE


def get_connection():
    conn = sqlite3.connect(DATABASE)
    return conn


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            category TEXT,
            brand TEXT,
            model TEXT,
            price REAL,
            quantity INTEGER
        )
    """)

    # Activity Log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    # NEW: Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    # Create default admin only if it does not already exist
    cursor.execute(
        "SELECT * FROM admin WHERE username = ?",
        ("admin",)
    )

    admin = cursor.fetchone()

    if admin is None:
        cursor.execute(
            "INSERT INTO admin(username, password) VALUES(?, ?)",
            ("admin", "1234")
        )

    conn.commit()
    conn.close()