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
    
def add_room(room_number, room_capacity, room_facilities, room_status):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO rooms (room_number, room_capacity, room_facilities, room_status) VALUES (?, ?, ?, ?)", (room_number, room_capacity, room_facilities, room_status))
        conn.commit()
        return f"Room {room_number} added successfully."
    except sqlite3.IntegrityError:
        return "Room already exists."
    finally:
        conn.close()

def update_room(room_number, room_capacity=None, room_facilities=None, room_status=None):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        updates = []
        values = []

        if room_capacity is not None:
            updates.append("room_capacity = ?")
            values.append(room_capacity)

        if room_facilities is not None:
            updates.append("room_facilities = ?")
            values.append(room_facilities)

        if room_status is not None:
            updates.append("room_status = ?")
            values.append(room_status)

        if not updates:
            return "No update values provided."

        values.append(room_number)
        update_query = f"UPDATE rooms SET {', '.join(updates)} WHERE room_number = ?"

        cursor.execute(update_query, values)
        conn.commit()

        if cursor.rowcount == 0:
            return f"No room found with number {room_number}."
        return f"Room {room_number} updated successfully."

    finally:
        conn.close()

def view_rooms():
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    conn.close()

    if not rooms:
        return "No rooms available."
    
    return rooms

#testing
print(add_user("ash1542", "ashmielqayyiem1542@gmail.com", "ayamas"))

print(login("ash1542", "ayamas"))

print(add_room("CQAR1002", "40" ,"projector,tv,whiteboard", "ready"))