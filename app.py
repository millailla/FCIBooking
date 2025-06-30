from flask import Flask, get_flashed_messages, render_template, request, redirect, url_for, flash, session
import sqlite3
from admin import admin_cancel_booking
from sql_function import delete_room, add_room, update_room_in_db
from sql_function import login as login_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def add_user(username, email, password, role='user'):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    try:
        is_approved = 1 if role == 'user' else 0
        cursor.execute("INSERT INTO users(username, email, password, role, is_approved) VALUES (?, ?, ?, ?, ?)", 
                      (username, email, password, role, is_approved))
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
    return user

def get_user_role(username):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_approved FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1]
    return None, None

def add_booking(username, room_number, booking_date, start_time, end_time):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bookings(username, room_number, date, start_time, end_time) VALUES (?, ?, ?, ?,?)", 
                     (username, room_number, booking_date, start_time, end_time))
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
        user_role = get_user_role(session['username'])[0]
    return render_template('index.html', messages=messages, user_role=user_role)  

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin' or session.get('is_approved') != 1:
        flash('Access denied: Admins only.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    # Get bookings
    cursor.execute("""
        SELECT b.id, b.username, b.room_number, b.date, b.start_time, b.end_time
        FROM bookings b
        ORDER BY b.date, b.start_time
    """)
    bookings = cursor.fetchall()

    # 🔑 Get rooms list from DB
    cursor.execute("""
        SELECT room_number, room_capacity, room_facilities, room_status
        FROM rooms
        ORDER BY room_number
    """)
    rooms = cursor.fetchall()

    conn.close()

    # 🔑 Make sure both are passed to the template!
    return render_template('admin.html', bookings=bookings, rooms=rooms)

@app.route('/admin/cancel-booking/<int:booking_id>', methods=['POST'])
def admin_cancel_booking(booking_id):
    if 'username' not in session or session.get('role') != 'admin' or not session.get('is_approved'):
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

    flash(f'Booking ID {booking_id} cancelled successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/book-now', methods=['GET', 'POST'])
def book_now():
    if 'username' not in session:
        return redirect('/login')

    rooms = get_available_rooms()

    if request.method == 'POST':
        room_number = request.form['room_number']
        booking_date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        username = session['username']

        # Validate time order
        if start_time >= end_time:
            flash("End time must be after start time.", "error")
            return redirect('/book-now')

        # Check room availability
        if is_room_booked(room_number, booking_date, start_time, end_time):
            flash('Booking unsuccessful! The room is occupied at that time.', 'error')
            return redirect(url_for('book_now'))

        # Attempt to add the booking
        if add_booking(username, room_number, booking_date, start_time, end_time):
            flash('Booking successful!', 'success')
            return redirect('/index')
        else:
            flash('Failed to book the room. Please try again.', 'error')

    return render_template('booknow.html', rooms=rooms)

def is_room_booked(room_number, booking_date, start_time, end_time):
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM bookings
        WHERE room_number = ? AND date = ? AND (
            (? < end_time AND ? > start_time)
        )
    """, (room_number, booking_date, start_time, end_time))
    
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

    cursor.execute("""
        SELECT room_number, date, start_time, end_time FROM bookings WHERE username = ? ORDER BY date, start_time""", (username,))
    
    bookings = cursor.fetchall()
    conn.close()

    bookings_list = [
        {
            'room_number': b[0],
            'date': b[1],
            'start_time': b[2],
            'end_time': b[3]
        } for b in bookings
    ]

    # Pass to template
    return render_template('my_bookings.html', bookings=bookings_list)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contacts', methods=['GET'])
def contact():
    return render_template('contacts.html')

@app.route('/rooms', methods=['GET'])
def rooms():
    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, room_capacity, room_facilities, room_status FROM rooms")
    rooms = cursor.fetchall()
    conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/register', methods=['GET', 'POST'])
def register():
    next_page = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
        elif add_user(username, email, password, role):
            flash('Sign up successful!' + (' Admin registration requires approval.' if role == 'admin' else ''), 'success')
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

        user_data, message = login_user(username, password)
        if user_data:
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            session['is_approved'] = True
            flash(message, 'success')

            if session['role'] == 'admin' and session['is_approved']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('index'))
        else:
            flash(message, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect('/index')

@app.route('/admin/add-room', methods=['POST'])
def add_room_route():
    if session.get('role') != 'admin' or session.get('is_approved') != 1:
        flash("Access denied. Admin login required.", "error")
        return redirect(url_for('login'))

    # Get form data
    room_number = request.form['room_number']
    room_capacity = request.form['capacity']
    room_facilities = ', '.join(request.form.getlist('features'))
    room_status = "available"

    conn = sqlite3.connect("booking_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
    existing_room = cursor.fetchone()
    conn.close()

    if existing_room:
        flash(f"Room {room_number} already exists. Please recheck and reconfirm room that want to be added.", "error")
        return redirect(url_for('admin_dashboard'))

    # Proceed to add the room
    result = add_room(room_number, room_capacity, room_facilities, room_status, session['role'])

    flash(result, "success" if "successfully" in result.lower() else "error")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-room', methods=['POST'])
def delete_room_route():
    if 'username' not in session:
        flash("Please log in.", "error")
        return redirect(url_for("login"))

    role, is_approved = get_user_role(session['username'])
    if role != "admin" or not is_approved:
        flash("Access denied.", "error")
        return redirect(url_for("index"))

    room_number = request.form.get("room_number")
    message = delete_room(room_number, role)
    flash(message, "success")
    return redirect(url_for("admin_dashboard"))

@app.route('/admin/update-room', methods=['GET', 'POST'])
def update_room():
    if session.get('role') != 'admin' or session.get('is_approved') != 1:
        flash("Access denied: Admins only.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_capacity = request.form.get('room_capacity')
        room_status = request.form.get('room_status')
        features = request.form.getlist('features')

        room_facilities = ', '.join(features) if features else None
        room_capacity = int(room_capacity) if room_capacity else None
        room_status = room_status if room_status else None

        # ✅ Use the renamed DB function here
        result = update_room_in_db(
            room_number=room_number,
            room_capacity=room_capacity,
            room_facilities=room_facilities,
            room_status=room_status,
            user_role=session.get('role')
        )
        flash(result, 'success' if "successfully" in result else 'error')
        return redirect('/admin/update-room')

    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
















 
