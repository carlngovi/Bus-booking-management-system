# server/app.py
import os
from flask_bcrypt import Bcrypt
from flask import Flask, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_restful import Resource
from dotenv import load_dotenv
from config import app, db, api
from models import db, User, Bus, Booking, Review, Route

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


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
    role = request_json.get('role')

    if not all([username, email, password, role]):
        return jsonify({'error': '400 Bad Request', 'message': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '422 Unprocessable Entity', 'message': 'Username already exists'}), 422

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '422 Unprocessable Entity', 'message': 'Email already exists'}), 422

    user = User(
        username=username,
        email=email,
        role=role,
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

# Endpoint to get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Endpoint to get all buses
@app.route('/buses', methods=['GET'])
def get_buses():
    buses = Bus.query.all()
    return jsonify([bus.to_dict() for bus in buses])

# Endpoint to get all bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([booking.to_dict() for booking in bookings])

# Endpoint to get all reviews
@app.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    return jsonify([review.to_dict() for review in reviews])

# Endpoint to get all routes
@app.route('/routes', methods=['GET'])
def get_routes():
    routes = Route.query.all()
    return jsonify([route.to_dict() for route in routes])


if __name__ == '__main__':
    app.run(port=5555, debug=True)
