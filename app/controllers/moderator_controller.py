# app/controllers/user_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app import jwt

# Import routes directly in the controller
# from app import routes

@jwt_required()
def get_moderators():
    moderators = User.query.filter_by(role='moderator').all()
    result = []
    for moderator in moderators:
        moderator_data = {
            "user_id": moderator.user_id,
            "username": moderator.username,
            "email": moderator.email,
            "role": moderator.role
        }
        result.append(moderator_data)
    return jsonify(result)

@jwt_required()
def create_moderator():
    if request.method == 'POST':
        # Extract data from the request JSON
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        nature = data.get('nature')
        # role = data.get('role', 'moderator')  # Default role is 'moderator' if not provided

        # Check if the email is already in use
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email address already in use. Please use a different email.'}), 400

        # Hash the password before storing it in the database
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user
        new_user = User(            
            username=username,
            email=email,
            password_hash=password_hash,
            firstName=firstName,
            lastName=lastName,
            nature=nature,
            role='moderator')

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Moderator created successfully.'}), 201

    return jsonify({'message': 'Signup endpoint. Please use POST method to signup.'})