import sqlite3


def is_admin():
    return session.get("role") == "admin"

def add_user(username, email, password, role="user"):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users(username, email, password, role, is_approved) VALUES (?, ?, ?, ?, ?)", (username, email, password, role, 0 if role == "admin" else 1))
        conn.commit()
        return "User added. Admins registration require admins approval"
    except sqlite3.IntegrityError:
       return "username already in use"
    finally:
       conn.close()

def login(username, password):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, role, is_approved FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        if user[1] == "admin" and user[2] == 0:
            return "Admin account is not yet approved."
        return {"username": user[0], "role": user[1]}, f"{user[0]} logged in as {user[1]}"
    else:
        return None,"Invalid username or password"
    
def log_out():
    global session
    if session["logged_in"]:
        user = session["logged_in"]
        session["logged_in"] = None
        return f"{user} logged out"
    else:
        return "no user logged in" 
    
def add_room(room_number, room_capacity, room_facilities, room_status, user_role):
    if user_role != "admin":
        return "Restricted access,please contact admin."
    
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

def update_room(room_number, room_capacity=None, room_facilities=None, room_status=None, user_role=None):
    if user_role != "admin":
        return "Restricted access,please contact admin"
    
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


def book_room(username, room_number, date, time):

    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT is_approved FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return "User does not exist."
        if user[0] == 0:
            return "User is not approved to make bookings."

        cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
        if not cursor.fetchone():
            return f"Room {room_number} does not exist."

        cursor.execute("""
            SELECT * FROM bookings
            WHERE room_number = ? AND date = ? AND time = ?
        """, (room_number, date, time))
        if cursor.fetchone():
            return f"Room {room_number} is already booked on {date} at {time}."

        cursor.execute("""
            INSERT INTO bookings (username, room_number, date, time)
            VALUES (?, ?, ?, ?)
        """, (username, room_number, date, time))
        conn.commit()

        return f"Room {room_number} successfully booked by {username} on {date} at {time}."

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        conn.close()

def delete_room(room_number, user_role):
    if user_role != "admin":
        return "Restricted access, please contact admin."

    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))

    conn.commit()
    conn.close()

    return f"Room {room_number} deleted."

def cancel_booking(username, booking_id):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings WHERE id = ? AND username = ?", (booking_id, username))
    booking = cursor.fetchone()

    if booking:
        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        result = f"Booking ID {booking_id} canceled successfully by user {username}."
    else:
        result = "Booking not found or you do not have permission to cancel it."

    conn.close()
    return result
#testing


print(login("ash1542", "ayamas"))
print(book_room("ash", "CQAR1001", "2025-06-15", "10:00"))