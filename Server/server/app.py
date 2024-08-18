# server/app.py
import os, firebase_admin, random, string
from flask import Flask, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db, User, Bus, Booking, Review, Route, ContactUs, Driver, Admin, Seat, PersnalDetails
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
@app.route('/')
def index():
    return 'Welcome to the TRANSITE WISE the Bus Booking App!'
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
    request_json = request.get_json()

    uid = request_json.get('uid')
    email = request_json.get('email')

    if not uid or not email:
        return jsonify({'message': 'UID and email are required'}), 400

    try:
        # Get user from Firebase using the UID
        user_record = auth.get_user(uid)
        
        # Optionally, get user from PostgreSQL if needed
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
    except auth.AuthError as e:
        return jsonify({'message': 'Error fetching user data from Firebase', 'error': str(e)}), 401

@app.route('/current_user', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user:
            return jsonify({
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.username,
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/current_driver', methods=['GET'])
@jwt_required()
def get_current_driver():
    try:
        current_driver_id = get_jwt_identity()
        current_driver = Driver.query.get(current_driver_id)

        if current_driver:
            return jsonify({
                'id': current_driver.id,
                'full_name': current_driver.full_name,
                'id_number': current_driver.id_number,
                'driving_license': current_driver.driving_license,
                'phone_number': current_driver.phone_number
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    
@app.route('/current_admin', methods=['GET'])
@jwt_required()
def get_current_admin():
    try:
        current_admin_id = get_jwt_identity()
        current_admin = Admin.query.get(current_admin_id)

        if current_admin:
            return jsonify({
                'id': current_admin.id,
                'full_name': current_admin.full_name,
                'id_number': current_admin.id_number,
                'phone_number': current_admin.phone_number
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
    
# Endpoint to manage drivers
@app.route('/drivers', methods=['GET', 'POST'])
def manage_drivers():
    if request.method == 'GET':
        drivers = Driver.query.all()
        return jsonify([driver.to_dict() for driver in drivers])
    
    elif request.method == 'POST':
        data = request.json

        # Validate input data
        if not all(key in data for key in ['full_name', 'id_number', 'driving_license', 'phone_number']):
            return jsonify({'error': 'Missing data'}), 400

        # Create new driver
        new_driver = Driver(
            full_name=data['full_name'],
            id_number=data['id_number'],
            driving_license=data['driving_license'],
            phone_number=data['phone_number']
        )

        try:
            db.session.add(new_driver)
            db.session.commit()
            return jsonify(new_driver.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/drivers/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_driver(id):
    driver = Driver.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(driver.to_dict())
    
    elif request.method == 'PATCH':
        data = request.json
        if 'full_name' in data:
            driver.full_name = data['full_name']
        if 'id_number' in data:
            driver.id_number = data['id_number']
        if 'driving_license' in data:
            driver.driving_license = data['driving_license']
        if 'phone_number' in data:
            driver.phone_number = data['phone_number']
        db.session.commit()
        return jsonify(driver.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(driver)
        db.session.commit()
        return '', 204
    
# Endpoint to manage admins
@app.route('/admins', methods=['GET', 'POST'])
def manage_admins():
    if request.method == 'GET':
        admins = Admin.query.all()
        return jsonify([admin.to_dict() for admin in admins])
    elif request.method == 'POST':
        data = request.json
        new_admin = Admin(
            full_name=data['full_name'],
            id_number=data['id_number'],
            phone_number=data['phone_number']
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify(new_admin.to_dict()), 201
    
@app.route('/admins/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_admin(id):
    admin = Admin.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(admin.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'full_name' in data:
            admin.full_name = data['full_name']
        if 'id_number' in data:
            admin.id_number = data['id_number']
        if 'phone_number' in data:
            admin.phone_number = data['phone_number']
        db.session.commit()
        return jsonify(admin.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(admin)
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
            seats_available=data['number_of_seats'],
            departure_from=data['departure_from'],
            departure_to=data['departure_to'],
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
        if 'seats_available' in data:
            bus.seats_available = data['seats_available']
        if 'departure_from' in data:
            bus.departure_from = data['departure_from']
        if 'departure_to' in data:
            bus.departure_to = data['departure_to']
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
    
# Endpoint to manage seats
@app.route('/seats', methods=['GET', 'POST', 'PATCH'])
def manage_seats():
    if request.method == 'GET':
        seats = Seat.query.all()
        return jsonify([seat.to_dict() for seat in seats])

    elif request.method == 'POST':
        data = request.json
        new_seat = Seat(
            bus_id=data['bus_id'],
            seat_number=data['seat_number'],
            status=data['status']
        )
        db.session.add(new_seat)
        db.session.commit()
        return jsonify(new_seat.to_dict()), 201

    elif request.method == 'PATCH':
        data = request.json
        seat_id = data.get('seat_id')
        new_status = data.get('status')

        if not seat_id or not new_status:
            return jsonify({'error': 'Invalid input'}), 400

        seat = Seat.query.get(seat_id)

        if not seat:
            return jsonify({'error': 'Seat not found'}), 404

        seat.status = new_status
        db.session.commit()

        return jsonify(seat.to_dict()), 200

# Endpoint to manage bookings
@app.route('/bookings', methods=['POST', 'GET'])
def manage_bookings():
    if request.method == 'POST':
        data = request.json
        if not all(field in data and data[field] for field in ['bus_id', 'seat_number', 'name', 'idNumber', 'phoneNumber']):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if bus exists
        bus = Bus.query.get(data['bus_id'])
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404

        # Check if seat is already booked
        existing_booking = Booking.query.filter_by(bus_id=data['bus_id'], seat_number=data['seat_number']).first()
        if existing_booking:
            return jsonify({'message': 'Seat already booked'}), 409

        # Generate a unique ticket number
        def generate_ticket():
            while True:
                code = ''.join(random.choices(string.digits, k=5) + random.choices(string.ascii_uppercase, k=1))
                random.shuffle(list(code))
                existing_booking = Booking.query.filter_by(ticket=code).first()
                if not existing_booking:
                    return code

        # Create a new booking
        new_booking = Booking(
            bus_id=data['bus_id'],
            seat_number=data['seat_number'],
            name=data['name'],
            idNumber=data['idNumber'],
            phoneNumber=data['phoneNumber'],
            status=data['status'],
            ticket=generate_ticket()  # Generate a unique ticket
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify({
            'ticket': new_booking.ticket,
            'status': new_booking.status,
            'message': 'Booking confirmed'
        }), 201
    
    elif request.method == 'GET':
        bookings = Booking.query.all()
        return jsonify([booking.to_dict() for booking in bookings])


@app.route('/bookings/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_booking(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # Fetch the booking by ID
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
        # Ensure the current user is authorized to delete this booking
        if booking.user_id != current_user.id:
            return jsonify({'message': 'Unauthorized'}), 403

        # Delete the booking from the database
        db.session.delete(booking)
        db.session.commit()
        
        return '', 204


    
# Endpoint to manage Personal Details
@app.route('/personaldetails', methods=['GET', 'POST'])
def manage_personaldetails():
    if request.method == 'GET':
        personaldetails = PersnalDetails.query.all()
        return jsonify([personaldetail.to_dict() for personaldetail in personaldetails])
    elif request.method == 'POST':
        data = request.json
        new_personaldetail = PersnalDetails(
            full_name=data['name'],
            id_number=data['id_number'],
            phone_number=data['phone_number']
        )
        db.session.add(new_personaldetail)
        db.session.commit()
        return jsonify(new_personaldetail.to_dict()), 201

# Endpoint to manage reviews
@app.route('/reviews', methods=['GET', 'POST'])
def manage_reviews():
    if request.method == 'GET':
        reviews = Review.query.all()
        return jsonify([review.to_dict() for review in reviews])
    elif request.method == 'POST':
        data = request.json
        new_review = Review(
            name=data['name'],
            email=data['email'],
            review=data['review'],
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
        if 'name' in data:
            review.name = data['name']
        if 'email' in data:
            review.email = data['email']
        if 'review' in data:
            review.review = data['review']
        if 'rating' in data:
            review.rating = data['rating']
        db.session.commit()
        return jsonify(review.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(review)
        db.session.commit()
        return '', 204
    
# Endpoint to manage contactus
@app.route('/contact', methods=['GET', 'POST'])
def manage_contactus():
    if request.method == 'GET':
        contactus = ContactUs.query.all()
        return jsonify([contact.to_dict() for contact in contactus])
    elif request.method == 'POST':
        data = request.json
        new_contact = ContactUs(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify(new_contact.to_dict()), 201
    
@app.route('/contact/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_contact(id):
    contact = ContactUs.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(contact.to_dict())
    elif request.method == 'PATCH':
        data = request.json
        if 'name' in data:
            contact.name = data['name']
        if 'email' in data:
            contact.email = data['email']
        if 'message' in data:
            contact.message = data['message']
        db.session.commit()
        return jsonify(contact.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(contact)
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
        new_route = Route(
            route_name=data['route_name'],
            departure_to=data['departure_to'],
            departure_from=data['departure_from'],
            )
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
        if 'departure_to' in data:
            route.departure_to = data['departure_to']
        if 'departure_from' in data:
            route.departure_from = data['departure_from']
        db.session.commit()
        return jsonify(route.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(route)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(port=5555, debug=True)
