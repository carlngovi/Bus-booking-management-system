from datetime import datetime, timezone
from decimal import Decimal
from app import  db, app
from models import Bus

def seed_buses():
    buses = [
        {
            'driver_id': 1,
            'number_plate': 'ABC123',
            'number_of_seats': 50,
            'departure_from': 'New York',
            'departure_to': 'Boston',
            'departure_time': datetime(2024, 8, 15, 8, 0, 0, tzinfo=timezone.utc),
            'arrival_time': datetime(2024, 8, 15, 12, 0, 0, tzinfo=timezone.utc),
            'price_per_seat': Decimal('30.00'),
        },
        {
            'driver_id': 2,
            'number_plate': 'XYZ789',
            'number_of_seats': 40,
            'departure_from': 'San Francisco',
            'departure_to': 'Los Angeles',
            'departure_time': datetime(2024, 8, 20, 9, 0, 0, tzinfo=timezone.utc),
            'arrival_time': datetime(2024, 8, 20, 14, 0, 0, tzinfo=timezone.utc),
            'price_per_seat': Decimal('45.00'),
        },
        # Add more buses here
    ]

    for bus in buses:
        new_bus = Bus(
            driver_id=bus['driver_id'],
            number_plate=bus['number_plate'],
            number_of_seats=bus['number_of_seats'],
            seats_available=bus['number_of_seats'],  # Initialize seats available to number_of_seats
            departure_from=bus['departure_from'],
            departure_to=bus['departure_to'],
            departure_time=bus['departure_time'],
            arrival_time=bus['arrival_time'],
            price_per_seat=bus['price_per_seat'],
        )
        db.session.add(new_bus)
    
    db.session.commit()
    print("Seed data added to 'buses' table")

if __name__ == '__main__':
    # Create the Flask application
    # app = app()  # Ensure create_app() is your function to initialize your Flask app

    # Push an application context
    with app.app_context():
        seed_buses()
