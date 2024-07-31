from app import  db, app
from models import db, User, Bus, Booking, Review, Route
from datetime import datetime, timezone


with app.app_context():
    # Drop all tables
    db.drop_all()

    # Create all tables
    db.create_all()

    # Create sample users
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash='hashed_password_admin',
        role='admin',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    driver = User(
        username='driver1',
        email='driver1@example.com',
        password_hash='hashed_password_driver1',
        role='driver',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    customer = User(
        username='customer1',
        email='customer1@example.com',
        password_hash='hashed_password_customer1',
        role='customer',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Add users to the session
    db.session.add(admin)
    db.session.add(driver)
    db.session.add(customer)
    db.session.commit()

    # Create sample routes
    route1 = Route(
        route_name='Route 1',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    route2 = Route(
        route_name='Route 2',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Add routes to the session
    db.session.add(route1)
    db.session.add(route2)
    db.session.commit()

    # Create sample buses
    bus1 = Bus(
        driver_id=driver.id,
        number_plate='ABC123',
        number_of_seats=50,
        model='Model X',
        route='Route 1',
        departure_time=datetime.now(timezone.utc),
        arrival_time=datetime.now(timezone.utc),
        price_per_seat=10.5,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    bus2 = Bus(
        driver_id=driver.id,
        number_plate='XYZ789',
        number_of_seats=40,
        model='Model Y',
        route='Route 2',
        departure_time=datetime.now(timezone.utc),
        arrival_time=datetime.now(timezone.utc),
        price_per_seat=12.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Add buses to the session
    db.session.add(bus1)
    db.session.add(bus2)
    db.session.commit()

    # Create sample bookings
    booking1 = Booking(
        bus_id=bus1.id,
        customer_id=customer.id,
        seat_number=1,
        status='booked',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    booking2 = Booking(
        bus_id=bus2.id,
        customer_id=customer.id,
        seat_number=2,
        status='cancelled',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Add bookings to the session
    db.session.add(booking1)
    db.session.add(booking2)
    db.session.commit()

    # Create sample reviews
    review1 = Review(
        booking_id=booking1.id,
        review_text='Great service!',
        rating=5,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    review2 = Review(
        booking_id=booking2.id,
        review_text='Cancelled my trip.',
        rating=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Add reviews to the session
    db.session.add(review1)
    db.session.add(review2)
    db.session.commit()

    # Associate buses with routes
    bus1.routes.append(route1)
    bus2.routes.append(route2)
    db.session.commit()

    print("Database seeded successfully!")
