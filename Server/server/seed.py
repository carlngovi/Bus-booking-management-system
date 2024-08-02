import random
import string
from datetime import datetime, timedelta, timezone

from app import db, app
from models import User, Bus, Booking, Review, Route

def random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_digit_string(length=5):
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(length))

def generate_ticket():
    return random_digit_string(5) + random.choice(string.ascii_uppercase)

def seed_users():
    user1 = User(username='admin', email='admin@example.com', firebase_uid='adminUID')
    user1.password_hash = 'adminpassword'
    user2 = User(username='driver', email='driver@example.com', firebase_uid='driverUID')
    user2.password_hash = 'driverpassword'
    user3 = User(username='customer', email='customer@example.com', firebase_uid='customerUID')
    user3.password_hash = 'customerpassword'
    
    db.session.add_all([user1, user2, user3])
    db.session.commit()

def seed_routes():
    route1 = Route(route_name='Route 1')
    route2 = Route(route_name='Route 2')
    db.session.add_all([route1, route2])
    db.session.commit()

def seed_buses():
    bus1 = Bus(driver_id=2, number_plate='ABC123', number_of_seats=50, model='Model X', route='Route 1',
               departure_time=datetime.now(timezone.utc) + timedelta(hours=1), arrival_time=datetime.now(timezone.utc) + timedelta(hours=5), price_per_seat=20.5)
    bus2 = Bus(driver_id=2, number_plate='XYZ789', number_of_seats=60, model='Model Y', route='Route 2',
               departure_time=datetime.now(timezone.utc) + timedelta(hours=2), arrival_time=datetime.now(timezone.utc) + timedelta(hours=6), price_per_seat=25.0)
    
    db.session.add_all([bus1, bus2])
    db.session.commit()

def seed_bookings():
    booking1 = Booking(bus_id=1, customer_id=3, seat_number=1, status='booked', ticket=generate_ticket())
    booking2 = Booking(bus_id=2, customer_id=3, seat_number=2, status='booked', ticket=generate_ticket())
    
    db.session.add_all([booking1, booking2])
    db.session.commit()

def seed_reviews():
    review1 = Review(booking_id=1, review_text='Great ride!', rating=5)
    review2 = Review(booking_id=2, review_text='Comfortable journey.', rating=4)
    
    db.session.add_all([review1, review2])
    db.session.commit()

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        seed_users()
        seed_routes()
        seed_buses()
        seed_bookings()
        seed_reviews()

        print('Database seeded!')

if __name__ == '__main__':
    seed_database()
