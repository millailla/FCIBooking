import sqlite3

conn = sqlite3.connect("booking_database")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    room_number TEXT,
    date TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
)
""")

conn.commit()
conn.close

print("Database siap.")