# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, func
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt
import random, string

# Contains definitions of tables and associated schema constructs
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Create the Flask SQLAlchemy extension
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()

# Association table for the many-to-many relationship between Bus and Route
bus_routes = db.Table('bus_routes', metadata,
                      db.Column('bus_id', db.Integer, db.ForeignKey('buses.id'), primary_key=True),
                      db.Column('route_id', db.Integer, db.ForeignKey('routes.id'), primary_key=True))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': {
                'date': self.created_at.strftime('%Y-%m-%d'),
                'time': self.created_at.strftime('%H:%M:%S')
            } if self.created_at else None,
            'updated_at': {
                'date': self.updated_at.strftime('%Y-%m-%d'),
                'time': self.updated_at.strftime('%H:%M:%S')
            } if self.updated_at else None,

        }

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email} ', firebase_uid='{self.firebase_uid}')>"
    

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    driving_license = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #Relationships
    buses = db.relationship('Bus', backref='driver', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'id_number': self.id_number,
            'driving_license': self.driving_license,
            'phone_number': self.phone_number
        }

    def __repr__(self):
        return f"<Driver(id={self.id}, full_name='{self.full_name}', id_number='{self.id_number}', driving_license='{self.driving_license}', phone_number='{self.phone_number}')>"
    
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'id_number': self.id_number,
            'phone_number': self.phone_number
        }

    def __repr__(self):
        return f"<Admin(id={self.id}, full_name='{self.full_name}', id_number='{self.id_number}', phone_number='{self.phone_number}')>"

    
class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    number_plate = db.Column(db.String(20), unique=True, nullable=False)
    number_of_seats = db.Column(db.Integer, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    departure_from = db.Column(db.String(20), nullable = False )
    departure_to = db.Column(db.String(20), nullable = False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price_per_seat = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    #Relationships
    bookings = db.relationship('Booking', backref='bus', lazy=True)
    seats = db.relationship('Seat', backref='bus', lazy=True)
    routes = db.relationship('Route', secondary=bus_routes, backref='buses', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seats_available = self.number_of_seats

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'number_plate': self.number_plate,
            'number_of_seats': self.number_of_seats,
            'seats_available': self.seats_available,
            'departure_from': self.departure_from,
            'departure_to': self.departure_to,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'price_per_seat': str(self.price_per_seat),
            'created_at': {
                'date': self.created_at.strftime('%Y-%m-%d'),
                'time': self.created_at.strftime('%H:%M:%S')
            } if self.created_at else None,
            'updated_at': {
                'date': self.updated_at.strftime('%Y-%m-%d'),
                'time': self.updated_at.strftime('%H:%M:%S')
            } if self.updated_at else None
        }

    def __repr__(self):
        return f"<Bus(id={self.id}, number_plate='{self.number_plate}', number_of_seats={self.number_of_seats}, seats_available={self.seats_available}, departure_time='{self.departure_time}', arrival_time='{self.arrival_time}', price_per_seat='{self.price_per_seat}, departure_from='{self.departure_from}', departure_to='{self.departure_to}')>"
    
class Seat(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'seat_number': self.seat_number,
            'status': self.status,
            'bus_id': self.bus_id
        }
    
    def __repr__(self):
        return f"<Seat(id={self.id}, seat_number='{self.seat_number}', status='{self.status}, bus_id={self.bus_id}')>"
    
class PersnalDetails(db.Model):
    __tablename__ = 'personal_details'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'id_number': self.id_number,
            'phone_number': self.phone_number,
            'seat_number': self.seat_number
        }
    
    def __repr__(self):
        return f"<PersnalDetails(id={self.id}, full_name='{self.full_name}', id_number='{self.id_number}', phone_number='{self.phone_number}', seat_number='{self.seat_number}')>"
    
class ContactUs(db.Model):
    __tablename__ = 'contactus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'created_at': self.created_at
        }
    def __repr__(self):
        return f"<ContactForm(id={self.id}, name='{self.name}', email='{self.email}')>"
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    seat_number = db.Column(db.String, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='booked')  # 'booked', 'cancelled'
    name = db.Column(db.String(80), nullable=False)
    idNumber = db.Column(db.String(20), nullable=False)
    phoneNumber = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    ticket = db.Column(db.String(6), unique=True, nullable=False, default='')


    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'name': self.name,
            'idNumber': self.idNumber,
            'phoneNumber': self.phoneNumber,
            'seat_number': self.seat_number,
            'status': self.status,
            'created_at': {
                'date': self.created_at.strftime('%Y-%m-%d'),
                'time': self.created_at.strftime('%H:%M:%S')
            } if self.created_at else None,
            'updated_at': {
                'date': self.updated_at.strftime('%Y-%m-%d'),
                'time': self.updated_at.strftime('%H:%M:%S')
            } if self.updated_at else None,
            'ticket': self.ticket
        }

    def __repr__(self):
        return f"<Booking(id={self.id}, bus_id={self.bus_id}, name='{self.name}', idNumber='{self.idNumber}', phoneNumber='{self.phoneNumber}', seat_number={self.seat_number}, status='{self.status}', ticket='{self.ticket}')>"

    def book_seat(self):
        bus = Bus.query.get(self.bus_id)
        if bus and bus.seats_available > 0:
            bus.seats_available -= 1
            db.session.add(self)
            db.session.commit()
        else:
            raise ValueError("No available seats for this bus.")

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # '1-5'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'review': self.review,
            'rating': self.rating,
            'created_at': {
                'date': self.created_at.strftime('%Y-%m-%d'),
                'time': self.created_at.strftime('%H:%M:%S')
            } if self.created_at else None,
            'updated_at': {
                'date': self.updated_at.strftime('%Y-%m-%d'),
                'time': self.updated_at.strftime('%H:%M:%S')
            } if self.updated_at else None
        }

    def __repr__(self):
        return f"<Review(id={self.id}, name='{self.name}', email='{self.email}', review='{self.review}', rating={self.rating})>"

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    departure_from = db.Column(db.String(100), nullable=False)
    departure_to = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'route_name': self.route_name,
            'created_at': {
                'date': self.created_at.strftime('%Y-%m-%d'),
                'time': self.created_at.strftime('%H:%M:%S')
            } if self.created_at else None,
            'updated_at': {
                'date': self.updated_at.strftime('%Y-%m-%d'),
                'time': self.updated_at.strftime('%H:%M:%S')
            } if self.updated_at else None
        }

    def __repr__(self):
        return f"<Route(id={self.id}, route_name='{self.route_name}, departure_from={self.departure_from}, departure_to={self.departure_to}')>"
