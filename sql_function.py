import sqlite3


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

#testing
print(add_user("ash1542", "ashmielqayyiem1542@gmail.com", "ayamas"))