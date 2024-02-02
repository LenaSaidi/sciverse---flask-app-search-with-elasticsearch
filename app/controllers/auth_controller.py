# app/controllers/auth_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app
from app.models import User
from app import jwt
import re

def is_valid_email(email):
    # Email validation regex
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)


def is_strong_password(password):
    # Check if password is at least 8 characters long and contains at least one uppercase, one lowercase, and one digit
    return len(password) >= 8 and any(char.isupper() for char in password) \
        and any(char.islower() for char in password) and any(char.isdigit() for char in password)

def signup():
    if request.method == 'POST':
        # Extract data from the request JSON
        data = request.json
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        nature = data.get('nature')
        field = data.get('field')

        # Validate email format
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format.'}), 400

        # Check if the email is already in use
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email address already in use. Please use a different email.'}), 400

        # Validate password strength
        if not is_strong_password(password):
            return jsonify({'error': 'Password should be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.'}), 400

        # Validate password strength
        if not is_strong_password(password):
            return jsonify({'message': 'Password should be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.'}), 400

        # Hash the password before storing it in the database
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user
        new_user = User(            
            email=email,
            password_hash=password_hash,
            firstName=firstName,
            lastName=lastName,
            nature=nature,
            field=field,
            role='user'
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Return the newly created user data along with the success message
        user_data = {
            'id': new_user.user_id,
            'email': new_user.email,
            'firstName': new_user.firstName,
            'lastName': new_user.lastName,
            'nature': new_user.nature,
            'field': new_user.field,
            'role': new_user.role
        }

        return jsonify({'message': 'Account created successfully. You can now login.', 'user': user_data}), 201

    return jsonify({'error': 'Signup endpoint. Please use POST method to signup.'}), 405  # Method Not Allowed

# Signin endpoint (POST)
def signin():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        email = request.json.get('email', None)
        password = request.json.get('password', None)

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Create a JWT
            access_token = create_access_token(identity=user.user_id)

            # Include user information in the response
            user_info = {
                'id': user.user_id,
                'email': user.email,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'nature': user.nature,
                'field': user.field,
                'role': user.role
                # Include other user information as needed
            }

            # Return the access token and user information in the response
            return jsonify({'access_token': access_token, 'user': user_info}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({'error': 'Signin endpoint. Please use POST method to signin.'})


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


