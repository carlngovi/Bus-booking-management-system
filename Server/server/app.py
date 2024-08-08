import os, firebase_admin
from flask import Flask, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User, Bus, Booking, ContactUs, Route
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from firebase_admin import auth, initialize_app, credentials
import logging

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize extensions
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize Firebase Admin SDK
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
if not firebase_credentials_path:
    raise ValueError("FIREBASE_CREDENTIALS environment variable is not set")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Utility function to validate required fields
def validate_fields(fields, data):
    missing = [field for field in fields if field not in data or not data[field]]
    if missing:
        return jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400
    return None

# Endpoint to create a new user
@app.route('/signup', methods=['POST'])
def signup():
    request_json = request.get_json()
    required_fields = ['username', 'email', 'password']
    validation_error = validate_fields(required_fields, request_json)
    if validation_error:
        return validation_error

    username = request_json.get('username')
    email = request_json.get('email')
    password = request_json.get('password')

    try:
        # Create Firebase user
        user_record = auth.create_user(
            email=email,
            password=password
        )
        firebase_uid = user_record.uid

        # Create new user in PostgreSQL
        new_user = User(email=email, username=username, firebase_uid=firebase_uid)
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        return jsonify({'token': access_token}), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error registering user: {str(e)}")
        return jsonify({'message': 'Error registering user', 'error': str(e)}), 400

# Endpoint to login a user
@app.route('/login', methods=['POST'])
def login():
    request_json = request.get_json()
    required_fields = ['uid', 'email']
    validation_error = validate_fields(required_fields, request_json)
    if validation_error:
        return validation_error

    uid = request_json.get('uid')
    email = request_json.get('email')

    try:
        # Verify Firebase ID token instead of just using UID
        user_record = auth.get_user(uid)
        
        # Check if user exists in PostgreSQL
        user = User.query.filter_by(firebase_uid=uid).first()
        if user:
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'token': access_token,
                'user': {
                    'email': user_record.email,
                    'name': user.username
                }
            }), 200
        else:
            return jsonify({'message': 'User not found in database'}), 404
    except Exception as e:
        logging.error(f"Error logging in user: {str(e)}")
        return jsonify({'message': 'Error logging in user', 'error': str(e)}), 401

# Endpoint to get current logged-in user details
@app.route('/current_user', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user:
            return jsonify({
                'email': current_user.email,
                'name': current_user.username,
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error fetching current user: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Endpoint to logout a user
@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)  # Removes the user_id from the session if it exists
    return jsonify({}), 204

# Endpoint to manage users
@app.route('/users', methods=['GET', 'POST'])
@jwt_required()  # Ensure only logged-in users can manage users
def manage_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200

    elif request.method == 'POST':
        data = request.json
        validation_error = validate_fields(['username', 'email', 'password'], data)
        if validation_error:
            return validation_error

        new_user = User(
            username=data['username'],
            email=data['email'],
        )
        new_user.password_hash = data['password']
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def manage_user(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(user.to_dict()), 200

    elif request.method == 'PATCH':
        data = request.json
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'password' in data:
            user.password_hash = data['password']
        db.session.commit()
        return jsonify(user.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204
    
# Endpoint to manage buses
@app.route('/buses', methods=['GET', 'POST'])
@jwt_required()
def manage_buses():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    if request.method == 'GET':
        buses = Bus.query.all()
        return jsonify([bus.to_dict() for bus in buses]), 200

    elif request.method == 'POST':
        data = request.json
        validation_error = validate_fields(['driver_id', 'number_plate', 'number_of_seats', 'depatrture_from', 'depatrture_to', 'departure_time', 'arrival_time', 'price_per_seat'], data)
        if validation_error:
            return validation_error

        # Ensure driver exists
        driver = User.query.get(data['driver_id'])
        if not driver:
            return jsonify({'message': 'Driver not found'}), 404

        new_bus = Bus(
            driver_id=data['driver_id'],
            number_plate=data['number_plate'],
            number_of_seats=data['number_of_seats'],
            depatrture_from=data['depatrture_from'],
            depatrture_to=data['depatrture_to'],
            departure_time=data['departure_time'],
            arrival_time=data['arrival_time'],
            price_per_seat=data['price_per_seat']
        )
        db.session.add(new_bus)
        db.session.commit()
        return jsonify(new_bus.to_dict()), 201

@app.route('/buses/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def manage_bus(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    bus = Bus.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(bus.to_dict()), 200

    elif request.method == 'PATCH':
        data = request.json
        if 'driver_id' in data:
            bus.driver_id = data['driver_id']
        if 'number_plate' in data:
            bus.number_plate = data['number_plate']
        if 'number_of_seats' in data:
            bus.number_of_seats = data['number_of_seats']
        if 'depatrture_from' in data:
            bus.depatrture_from = data['depatrture_from']
        if 'depatrture_to' in data:
            bus.depatrture_to = data['depatrture_to']
        if 'departure_time' in data:
            bus.departure_time = data['departure_time']
        if 'arrival_time' in data:
            bus.arrival_time = data['arrival_time']
        if 'price_per_seat' in data:
            bus.price_per_seat = data['price_per_seat']
        db.session.commit()
        return jsonify(bus.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(bus)
        db.session.commit()
        return '', 204

# Endpoint to manage bookings
@app.route('/bookings', methods=['GET', 'POST'])
@jwt_required()
def manage_bookings():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if request.method == 'GET':
        bookings = Booking.query.filter_by(customer_id=current_user.id).all()
        return jsonify([booking.to_dict() for booking in bookings]), 200

    elif request.method == 'POST':
        data = request.json
        validation_error = validate_fields(['bus_id', 'seat_number'], data)
        if validation_error:
            return validation_error

        # Check if bus exists
        bus = Bus.query.get(data['bus_id'])
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404

        # Check if seat is already booked
        existing_booking = Booking.query.filter_by(bus_id=bus.id, seat_number=data['seat_number']).first()
        if existing_booking:
            return jsonify({'message': 'Seat already booked'}), 409

        # Book the seat
        new_booking = Booking(
            customer_id=current_user.id,
            bus_id=bus.id,
            seat_number=data['seat_number']
        )
        bus.number_of_seats -= 1  # Decrement seat count
        new_booking.generate_ticket()  # Generate a unique ticket
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.to_dict()), 201

@app.route('/bookings/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def manage_booking(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    booking = Booking.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(booking.to_dict()), 200

    elif request.method == 'PATCH':
        data = request.json
        if 'seat_number' in data:
            # Check if seat is already booked
            existing_booking = Booking.query.filter_by(bus_id=booking.bus_id, seat_number=data['seat_number']).first()
            if existing_booking:
                return jsonify({'message': 'Seat already booked'}), 409
            booking.seat_number = data['seat_number']
        db.session.commit()
        return jsonify(booking.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(booking)
        db.session.commit()
        return '', 204

# Endpoint to get all routes
@app.route('/routes', methods=['GET'])
def get_routes():
    routes = Route.query.all()
    return jsonify([route.to_dict() for route in routes]), 200

# Endpoint to contact us
@app.route('/contact', methods=['POST'])
def contact_us():
    data = request.json
    validation_error = validate_fields(['name', 'email', 'message'], data)
    if validation_error:
        return validation_error

    contact = ContactUs(
        name=data['name'],
        email=data['email'],
        message=data['message']
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify({'message': 'Thank you for contacting us!'}), 201

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
