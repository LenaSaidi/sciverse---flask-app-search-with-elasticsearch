# app/controllers/user_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app import jwt
from app.controllers.auth_controller import is_valid_email, is_strong_password

# Import routes directly in the controller
# from app import routes


def get_admins():
    admins = User.query.filter_by(role='admin').all()
    result = []
    for admin in admins:
        admin_data = {
            "user_id": admin.user_id,
            "username": admin.username,
            "email": admin.email,
            "role": admin.role
        }
        result.append(admin_data)
    return jsonify(result)

def create_admin():
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
            role='admin'
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

        return jsonify({'message': 'Admin created successfully. You can now login.', 'user': user_data}), 201

    return jsonify({'error': 'admin creation endpoint. Please use POST method to signup.'}), 405  # Method Not Allowed