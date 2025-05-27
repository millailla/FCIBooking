import sqlite3

def list_pending_admins():
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users WHERE role = 'admin' AND is_approved = 0")
    pending_admins = cursor.fetchall()
    conn.close()
    return pending_admins

def approve_admin(username):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = 1 WHERE username = ? AND role = 'admin'", (username,))
    conn.commit()
    conn.close()
    return f"{username} has been approved as admin."
