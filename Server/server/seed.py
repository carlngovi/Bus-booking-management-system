import random
import string
from datetime import datetime, timedelta, timezone

from app import db, app
from models import User, Bus, Booking, Review, Route, ContactUs

def random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_digit_string(length=5):
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(length))

def generate_ticket():
    return random_digit_string(5) + random.choice(string.ascii_uppercase)


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
    review1 = Review(name='John Doe', email='john@example.com', review='Great service!', rating=5)
    review2 = Review(name='Jane Smith', email='jane@example.com', review='Very comfortable ride.', rating=4)
    review3 = Review(name='Alice Jones', email='alice@example.com', review='The bus was on time and very comfortable.', rating=4)
    
    db.session.add_all([review1, review2, review3])
    db.session.commit()

def seed_contactus():
    contact1 = ContactUs(name='John Doe', email='john@example.com', message='Hello, I need help with my booking.')
    contact2 = ContactUs(name='Jane Smith', email='jane@example.com', message='I have a question about the routes.')
    contact3 = ContactUs(name='Alice Jones', email='alice@example.com', message='How can I cancel my booking?')
    
    db.session.add_all([contact1, contact2, contact3])
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
        seed_contactus()

        print('Database seeded!')

if __name__ == '__main__':
    seed_database()
