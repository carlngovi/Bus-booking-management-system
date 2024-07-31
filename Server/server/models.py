# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime, timezone

# Contains definitions of tables and associated schema constructs
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Create the Flask SQLAlchemy extension
db = SQLAlchemy(metadata=metadata)

# Association table for the many-to-many relationship between Bus and Route
bus_routes = db.Table('bus_routes', metadata,
                      db.Column('bus_id', db.Integer, db.ForeignKey('buses.id'), primary_key=True),
                      db.Column('route_id', db.Integer, db.ForeignKey('routes.id'), primary_key=True))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'driver', 'customer'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    bookings = db.relationship('Booking', backref='user', lazy=True)
    buses = db.relationship('Bus', backref='driver', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    number_plate = db.Column(db.String(20), unique=True, nullable=False)
    number_of_seats = db.Column(db.Integer, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    route = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price_per_seat = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    bookings = db.relationship('Booking', backref='bus', lazy=True)
    routes = db.relationship('Route', secondary=bus_routes, backref='buses', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'number_plate': self.number_plate,
            'number_of_seats': self.number_of_seats,
            'model': self.model,
            'route': self.route,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'price_per_seat': str(self.price_per_seat),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Bus(id={self.id}, number_plate='{self.number_plate}', model='{self.model}', route='{self.route}')>"

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'booked', 'cancelled'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    review = db.relationship('Review', backref='booking', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'customer_id': self.customer_id,
            'seat_number': self.seat_number,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Booking(id={self.id}, bus_id={self.bus_id}, customer_id={self.customer_id}, seat_number={self.seat_number}, status='{self.status}')>"

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # '1-5'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'review_text': self.review_text,
            'rating': self.rating,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Review(id={self.id}, booking_id={self.booking_id}, rating={self.rating})>"

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'route_name': self.route_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Route(id={self.id}, route_name='{self.route_name}')>"
