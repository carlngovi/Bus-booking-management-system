# server/app.py
import os, firebase_admin
from flask import Flask, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User, Bus, Booking, Review, Route
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from firebase_admin import auth, initialize_app, credentials

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

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


# Endpoint to create a new user

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login',
        'check_session'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
         return {'error': '401 Unauthorized'}, 401
    
@app.route('/signup', methods=['POST'])
def signup():
    request_json = request.get_json()

    username = request_json.get('username')
    email = request_json.get('email')
    password = request_json.get('password')

    if not email or not password or not username:
        return jsonify({'message': 'Email, password, and username are required'}), 400
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
        return jsonify({'message': 'Error registering user', 'error': str(e)}), 400

    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        # Verify Firebase user
        user = auth.get_user_by_email(email)
        firebase_uid = user.uid

        # Get user from PostgreSQL
        user = User.query.filter_by(firebase_uid=firebase_uid).first()

        if user:
            access_token = create_access_token(identity=user.id)
            return jsonify({'token': access_token}), 200
        else:
            return jsonify({'message': 'User not found in database'}), 404

    except Exception as e:
        return jsonify({'message': 'Invalid credentials', 'error': str(e)}), 401

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
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500



@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)  # Removes the user_id from the session if it exists
    
    return jsonify({}), 204

# Endpoint to manage users
@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    elif request.method == 'POST':
        data = request.json
        new_user = User(
            username=data['username'],
            email=data['email'],
            role=data['role']
        )
        new_user.password_hash = data['password']
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(user.to_dict())
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
        return jsonify(user.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204

# Endpoint to manage buses
@app.route('/buses', methods=['GET', 'POST'])
def manage_buses():
    if request.method == 'GET':
        buses = Bus.query.all()
        return jsonify([bus.to_dict() for bus in buses])
    elif request.method == 'POST':
        data = request.json
        new_bus = Bus(
            driver_id=data['driver_id'],
            number_plate=data['number_plate'],
            number_of_seats=data['number_of_seats'],
            model=data['model'],
            route=data['route'],
            departure_time=data['departure_time'],
            arrival_time=data['arrival_time'],
            price_per_seat=data['price_per_seat']
        )
        db.session.add(new_bus)
        db.session.commit()
        return jsonify(new_bus.to_dict()), 201

@app.route('/buses/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_bus(id):
    bus = Bus.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(bus.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'driver_id' in data:
            bus.driver_id = data['driver_id']
        if 'number_plate' in data:
            bus.number_plate = data['number_plate']
        if 'number_of_seats' in data:
            bus.number_of_seats = data['number_of_seats']
        if 'model' in data:
            bus.model = data['model']
        if 'route' in data:
            bus.route = data['route']
        if 'departure_time' in data:
            bus.departure_time = data['departure_time']
        if 'arrival_time' in data:
            bus.arrival_time = data['arrival_time']
        if 'price_per_seat' in data:
            bus.price_per_seat = data['price_per_seat']
        db.session.commit()
        return jsonify(bus.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(bus)
        db.session.commit()
        return '', 204

# Endpoint to manage bookings
@app.route('/bookings', methods=['GET', 'POST'])
@jwt_required()
def manage_bookings():
    current_user_id = get_jwt_identity()

    if request.method == 'GET':
        bookings = Booking.query.filter_by(customer_id=current_user_id).all()
        return jsonify([booking.to_dict() for booking in bookings]), 200

    elif request.method == 'POST':
        data = request.json
        new_booking = Booking(
            bus_id=data['bus_id'],
            customer_id=current_user_id,  # Use current_user_id instead of data['customer_id']
            seat_number=data['seat_number'],
            status=data['status']
        )
        new_booking.generate_ticket()
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.to_dict()), 201

@app.route('/bookings/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def manage_booking(id):
    current_user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=id, customer_id=current_user_id).first_or_404()

    if request.method == 'GET':
        return jsonify(booking.to_dict()), 200
    elif request.method == 'PATCH':
        data = request.json
        if 'bus_id' in data:
            booking.bus_id = data['bus_id']
        if 'seat_number' in data:
            booking.seat_number = data['seat_number']
        if 'status' in data:
            booking.status = data['status']
        db.session.commit()
        return jsonify(booking.to_dict()), 200
    elif request.method == 'DELETE':
        db.session.delete(booking)
        db.session.commit()
        return '', 204
    
# Endpoint to manage bookings
@app.route('/adminbookings', methods=['GET', 'POST'])
def admin_bookings():
    if request.method == 'GET':
        bookings = Booking.query.all()
        return jsonify([booking.to_dict() for booking in bookings])
    elif request.method == 'POST':
        data = request.json
        new_booking = Booking(
            bus_id=data['bus_id'],
            customer_id=data['customer_id'],
            seat_number=data['seat_number'],
            status=data['status']
        )
        new_booking.generate_ticket()
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.to_dict()), 201

@app.route('/adminbookings/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def admin_booking(id):
    booking = Booking.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(booking.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'bus_id' in data:
            booking.bus_id = data['bus_id']
        if 'customer_id' in data:
            booking.customer_id = data['customer_id']
        if 'seat_number' in data:
            booking.seat_number = data['seat_number']
        if 'status' in data:
            booking.status = data['status']
        db.session.commit()
        return jsonify(booking.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(booking)
        db.session.commit()
        return '', 204

# Endpoint to manage reviews
@app.route('/reviews', methods=['GET', 'POST'])
def manage_reviews():
    if request.method == 'GET':
        reviews = Review.query.all()
        return jsonify([review.to_dict() for review in reviews])
    elif request.method == 'POST':
        data = request.json
        new_review = Review(
            booking_id=data['booking_id'],
            review_text=data['review_text'],
            rating=data['rating']
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify(new_review.to_dict()), 201

@app.route('/reviews/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_review(id):
    review = Review.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(review.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'booking_id' in data:
            review.booking_id = data['booking_id']
        if 'review_text' in data:
            review.review_text = data['review_text']
        if 'rating' in data:
            review.rating = data['rating']
        db.session.commit()
        return jsonify(review.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(review)
        db.session.commit()
        return '', 204

# Endpoint to manage routes
@app.route('/routes', methods=['GET', 'POST'])
def manage_routes():
    if request.method == 'GET':
        routes = Route.query.all()
        return jsonify([route.to_dict() for route in routes])
    elif request.method == 'POST':
        data = request.json
        new_route = Route(route_name=data['route_name'])
        db.session.add(new_route)
        db.session.commit()
        return jsonify(new_route.to_dict()), 201

@app.route('/routes/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_route(id):
    route = Route.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(route.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'route_name' in data:
            route.route_name = data['route_name']
        db.session.commit()
        return jsonify(route.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(route)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(port=5555, debug=True)
