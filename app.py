from flask import Flask, get_flashed_messages, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def add_user(username, email, password):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return True  
    except sqlite3.IntegrityError:
        return False  
    except Exception as e:
        print(f"An error occurred while adding user: {e}")
        return False  
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_role(username):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def add_booking(username, room_number, booking_date, booking_time):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bookings(username, room_number, date, time) VALUES (?, ?, ?, ?)", 
                       (username, room_number, booking_date, booking_time))
        conn.commit()
        return True  
    except Exception as e:
        print(f"An error occurred while adding booking: {e}")
        return False  
    finally:
        conn.close()

@app.route('/')
def home():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
    messages = get_flashed_messages(with_categories=True)
    user_role = None
    if 'username' in session:
        user_role = get_user_role(session['username'])
    return render_template('index.html', messages=messages, user_role=user_role)  

@app.route('/admin')
def admin():
    if 'username' not in session:
        flash('Please log in as admin to access this page.', 'error')
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    if user_role != 'admin':
        flash('Access denied: Admins only.', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/book-now', methods=['GET', 'POST'])
def book_now():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        room_number = request.form['room_number']
        booking_date = request.form['date']
        booking_time = request.form['time']
        username = session['username']

        if is_room_booked(room_number, booking_date, booking_time):
            flash('Booking unsuccessful! The room is occupied at that time.', 'error')
            return redirect(url_for('book_now'))

        if add_booking(username, room_number, booking_date, booking_time):
            flash('Booking successful!', 'success')
            return redirect('/index')
        else:
            flash('Failed to book the room. Please try again.', 'error')

    rooms = get_available_rooms()
    return render_template('booknow.html', rooms=rooms)

def is_room_booked(room_number, booking_date, booking_time):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE room_number = ? AND date = ? AND time = ?", 
               (room_number, booking_date, booking_time))

    booking = cursor.fetchone()
    conn.close()
    return booking is not None

def get_available_rooms():
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_number FROM rooms")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

@app.route('/my-bookings', methods=['GET'])
def my_bookings():
    if 'username' not in session:
        flash('Please login to view your bookings.', 'error')
        return redirect('/login')
    username = session['username']
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, date, time FROM bookings WHERE username = ? ORDER BY date, time", (username,))
    bookings = cursor.fetchall()
    conn.close()
    # convert bookings to list of dicts for easier template use
    bookings_list = [{'room_number': b[0], 'date': b[1], 'time': b[2]} for b in bookings]
    return render_template('my_bookings.html', bookings=bookings_list)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contacts', methods=['GET'])
def contact():
    return render_template('contacts.html')

@app.route('/rooms', methods=['GET'])
def rooms():
    return render_template('rooms.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    next_page = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
        elif add_user(username, email, password):
            flash('Sign up successful!', 'success')
            return redirect(next_page or '/index')
        else:
            flash('Username already in use. Please try again.', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(next_page or '/index')
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)













 
