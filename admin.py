import sqlite3

def admin_cancel_booking(booking_id, admin_username):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE username = ?", (admin_username,))
    user = cursor.fetchone()

    if not user or user[0] != "admin":
        conn.close()
        return "Permission denied. Only admins can cancel other users' bookings."

    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = cursor.fetchone()

    if booking:
        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        result = f"Booking ID {booking_id} canceled by admin {admin_username}."
    else:
        result = "Booking not found."

    conn.close()
    return result
