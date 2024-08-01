# server/app.py
import os
from flask import Flask, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import app, db
from models import db, User, Bus, Booking, Review, Route

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)


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

    if not all([username, email, password]):
        return jsonify({'error': '400 Bad Request', 'message': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '422 Unprocessable Entity', 'message': 'Username already exists'}), 422

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '422 Unprocessable Entity', 'message': 'Email already exists'}), 422

    user = User(
        username=username,
        email=email,
    )

    # Set the password hash using the setter
    user.password_hash = password

    try:
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return jsonify(user.to_dict()), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '422 Unprocessable Entity', 'message': 'Invalid data'}), 422
    
@app.route('/login', methods=['POST'])
def login():
    request_json = request.get_json()
    username = request_json.get('username')
    password = request_json.get('password')

    if not username or not password:
        return jsonify({'error': '400 Bad Request', 'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.authenticate(password):
        session['user_id'] = user.id
        return jsonify(user.to_dict()), 200

    return jsonify({'error': '401 Unauthorized', 'message': 'Invalid username or password'}), 401


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
def manage_bookings():
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

@app.route('/bookings/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_booking(id):
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
