# app/controllers/auth_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app import jwt
from app import login_manager

# Import routes directly in the controller
# from app import routes


def signup():

    if request.method == 'POST':
        # Extract data from the request JSON
        data = request.json
        # username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        nature = data.get('nature')
        # role = data.get('role', 'user')  # Default role is 'user' if not provided

        # Check if the email is already in use
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email address already in use. Please use a different email.'}), 400

        # Hash the password before storing it in the database
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user
        new_user = User(            
            # username=username,
            email=email,
            password_hash=password_hash,
            firstName=firstName,
            lastName=lastName,
            nature=nature,
            role='user')

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Account created successfully. You can now login.'}), 201

    return jsonify({'message': 'Signup endpoint. Please use POST method to signup.'})

# Signin endpoint (POST)
def signin():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        email = request.json.get('email', None)
        password = request.json.get('password', None)

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Create a JWT
            access_token = create_access_token(identity=user.user_id)  
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Invalid email or password"}), 401

    return jsonify({'message': 'Signin endpoint. Please use POST method to signin.'})

# Signout endpoint (POST)
@jwt_required()
def signout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

# Example protected route
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


