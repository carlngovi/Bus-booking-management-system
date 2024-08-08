from models import db, User, Bus, Route, Booking, Review, ContactUs
from app import app
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import auth

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app()

def create_firebase_user(email, password):
    try:
        user_record = auth.create_user(email=email, password=password)
        return user_record.uid
    except Exception as e:
        print(f"Error creating Firebase user for {email}: {e}")
        return None

def seed_users():
    print("Seeding users...")
    users = [
        {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123'},
        {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123'},
        {'username': 'jane_doe', 'email': 'jane@example.com', 'password': 'password123'},
    ]
    
    for user_data in users:
        firebase_uid = create_firebase_user(user_data['email'], user_data['password'])
        if firebase_uid:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                firebase_uid=firebase_uid,
            )
            db.session.add(user)
    
    db.session.commit()
    print("Users seeded.")

def seed_routes():
    print("Seeding routes...")
    routes = [
        {'route_name': 'New York to Boston', 'departure_from': 'New York', 'departure_to': 'Boston'},
        {'route_name': 'Los Angeles to San Francisco', 'departure_from': 'Los Angeles', 'departure_to': 'San Francisco'},
        {'route_name': 'Chicago to Detroit', 'departure_from': 'Chicago', 'departure_to': 'Detroit'},
    ]
    
    for route_data in routes:
        route = Route(
            route_name=route_data['route_name'],
            departure_from=route_data['departure_from'],
            departure_to=route_data['departure_to'],
        )
        db.session.add(route)
    
    db.session.commit()
    print("Routes seeded.")

def seed_buses():
    print("Seeding buses...")
    buses = [
        {'driver_id': 1, 'number_plate': 'ABC123', 'number_of_seats': 50, 'depatrture_from': 'New York', 'depatrture_to': 'Boston', 'departure_time': datetime.now(timezone.utc) + timedelta(days=1), 'arrival_time': datetime.now(timezone.utc) + timedelta(days=1, hours=4), 'price_per_seat': 100.0},
        {'driver_id': 2, 'number_plate': 'XYZ789', 'number_of_seats': 30, 'depatrture_from': 'Los Angeles', 'depatrture_to': 'San Francisco', 'departure_time': datetime.now(timezone.utc) + timedelta(days=2), 'arrival_time': datetime.now(timezone.utc) + timedelta(days=2, hours=4), 'price_per_seat': 120.0},
        {'driver_id': 3, 'number_plate': 'LMN456', 'number_of_seats': 40, 'depatrture_from': 'Chicago', 'depatrture_to': 'Detroit', 'departure_time': datetime.now(timezone.utc) + timedelta(days=3), 'arrival_time': datetime.now(timezone.utc) + timedelta(days=3, hours=4), 'price_per_seat': 80.0},
    ]
    
    for bus_data in buses:
        bus = Bus(
            driver_id=bus_data['driver_id'],
            number_plate=bus_data['number_plate'],
            number_of_seats=bus_data['number_of_seats'],
            depatrture_from=bus_data['depatrture_from'],
            depatrture_to=bus_data['depatrture_to'],
            departure_time=bus_data['departure_time'],
            arrival_time=bus_data['arrival_time'],
            price_per_seat=bus_data['price_per_seat']
        )
        db.session.add(bus)
    
    db.session.commit()
    print("Buses seeded.")

def seed_bookings():
    print("Seeding bookings...")
    bookings = [
        {'bus_id': 1, 'customer_id': 2, 'seat_number': 5},
        {'bus_id': 1, 'customer_id': 2, 'seat_number': 10},
        {'bus_id': 2, 'customer_id': 3, 'seat_number': 15},
        {'bus_id': 2, 'customer_id': 3, 'seat_number': 20},
    ]
    
    for booking_data in bookings:
        booking = Booking(
            bus_id=booking_data['bus_id'],
            customer_id=booking_data['customer_id'],
            seat_number=booking_data['seat_number'],
        )
        booking.generate_ticket()
        booking.book_seat()
        db.session.add(booking)
    
    db.session.commit()
    print("Bookings seeded.")

def seed_reviews():
    print("Seeding reviews...")
    reviews = [
        {'name': 'John Doe', 'email': 'john@example.com', 'review': 'Great service!', 'rating': 5},
        {'name': 'Jane Doe', 'email': 'jane@example.com', 'review': 'Comfortable ride.', 'rating': 4},
        {'name': 'Mark Smith', 'email': 'mark@example.com', 'review': 'Could be better.', 'rating': 3},
    ]
    
    for review_data in reviews:
        review = Review(
            name=review_data['name'],
            email=review_data['email'],
            review=review_data['review'],
            rating=review_data['rating'],
        )
        db.session.add(review)
    
    db.session.commit()
    print("Reviews seeded.")

def seed_contact_us():
    print("Seeding contact us messages...")
    messages = [
        {'name': 'John Doe', 'email': 'john@example.com', 'message': 'I had an issue with my booking.'},
        {'name': 'Jane Doe', 'email': 'jane@example.com', 'message': 'How do I cancel my booking?'},
        {'name': 'Mark Smith', 'email': 'mark@example.com', 'message': 'I lost my ticket. What should I do?'},
    ]
    
    for message_data in messages:
        message = ContactUs(
            name=message_data['name'],
            email=message_data['email'],
            message=message_data['message'],
        )
        db.session.add(message)
    
    db.session.commit()
    print("Contact Us messages seeded.")

def main():
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_users()
        seed_routes()
        # seed_buses()
        seed_bookings()
        seed_reviews()
        seed_contact_us()

if __name__ == '__main__':
    main()
