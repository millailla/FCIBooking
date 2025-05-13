import sqlite3

session = {"logged_in": None}

def add_user(username, email, password):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users(username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return "user added"
    except sqlite3.IntegrityError:
       return "username already in use"
    finally:
       conn.close()

def login(username, password):
    global session
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        session ["logged_in"] = username
        return f"{username} logged in"
    else:
        return "Invalid username or password"
    
def log_out():
    global session
    if session["logged_in"]:
        user = session["logged_in"]
        session["logged_in"] = None
        return f"{user} logged out"
    else:
        return "no user logged in" 
    
def add_room(room_number):
    """Add a room to the rooms table."""
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO rooms (room_number) VALUES (?)", (room_number,))
        conn.commit()
        return f"Room {room_number} added successfully."
    except sqlite3.IntegrityError:
        return "Room already exists."
    finally:
        conn.close()

#testing
print(add_user("ash1542", "ashmielqayyiem1542@gmail.com", "ayamas"))

print(login("ash1542", "ayamas"))