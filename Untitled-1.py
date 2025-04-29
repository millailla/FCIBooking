class booking_system:
    
    def book_room(username, room_number, date):
        for booking in bookings :
            if booking["room_number"] == room_number and booking["date"] == date:
                return "Room is unavailable"
        bookings.append({"username": username, "room_number": room_number, "date": date})
        return "Room booked"
    
    def cancel_booking(username, room_number, date):
        for booking in bookings:
            if (booking["username"] == username and 
                booking["room_number"] == room_number and 
                booking["date"] == date):
                bookings.remove(booking)
                return "Booking Cancelled"
        return "Booking not found"
    
    def view_my_booking(username):
        user_booking = []
        for booking in bookings:
            if bookings["username"] == username:
                user_booking.append(booking)
        return user_bookings
    
    def view_available_room(date):
        for room in rooms:
            booked = False
            for booking in bookings:
                if booking["room_number"] == room["room_name"] and booking["date"] == date:
                    booked = True
                    break
            if not booked:
                available.append(room["room_number"])


class admin:
    def add_room(room_number)
        for room in rooms:
            if room["room_number"] == room_number:
            return "room already added"
        rooms.append ({"room_number" : room_number})
        return "room added"
    
    def delete_room(room_number)
        for room in rooms:
            if room["room_number"] == room_number:
                rooms.delete (room)
                return "room deleted"
        return "room not found"