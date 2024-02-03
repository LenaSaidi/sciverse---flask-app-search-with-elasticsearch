# app/controllers/user_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app import jwt
from app.controllers.auth_controller import is_strong_password



@jwt_required()
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {
        "user_id": user.user_id,
        "password_hash": user.password_hash,
        "email": user.email,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "nature": user.nature,
        "role": user.role,
        "field": user.field
        }
        result.append(user_data)
    return jsonify(result)


@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        "user_id": user.user_id,
        "password_hash": user.password_hash,
        "email": user.email,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "nature": user.nature,
        "field": user.field,
        "role": user.role
    }
    return jsonify(user_data)



@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json

    # Define the attributes to update
    update_fields = {
        'email': data.get('email', user.email),
        'firstName': data.get('firstName', user.firstName),
        'lastName': data.get('lastName', user.lastName),
        'nature': data.get('nature', user.nature),
        'role': data.get('role', user.role),
        'field': data.get('field', user.field),
    }

    # Check if the new email exists for another user
    new_email = update_fields['email']
    existing_user_with_email = User.query.filter(User.email == new_email, User.user_id != user_id).first()
    if existing_user_with_email:
        return jsonify({'error': 'Email already exists. Please use a different email.'}), 400

    # Update the user attributes
    for field, value in update_fields.items():
        # Skip updating if the value is an empty string or None
        if value != '' and value is not None:
            setattr(user, field, value)

    # Update the password if a new one is provided and it's a strong password
    new_password = data.get('password')
    if new_password:
        if not is_strong_password(new_password):
            return jsonify({'error': 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.'}), 400
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

    db.session.commit()

    return jsonify({'message': 'User updated successfully'})


@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})


