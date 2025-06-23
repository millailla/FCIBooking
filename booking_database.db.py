import sqlite3

def setup_database():
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            password TEXT,
            role TEXT DEFAULT 'user',
            is_approved INTEGER DEFAULT 0
         )
     """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            room_number TEXT,
            date TEXT,
            time TEXT,
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(room_number) REFERENCES rooms(room_number)
         )
     """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_capacity TEXT,
            room_facilities TEXT,
            room_status TEXT
         )
     """)
     
    conn.commit()
    conn.close()


conn = sqlite3.connect("booking_database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE bookings ADD COLUMN start_time TEXT")

conn.commit()
conn.close()

if __name__ == "__main__":
    setup_database()