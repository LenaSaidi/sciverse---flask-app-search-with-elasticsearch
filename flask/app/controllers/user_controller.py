# app/controllers/user_controller.py

from flask import jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app import jwt

# Import routes directly in the controller
# from app import routes


def get_users():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {
        "user_id": user.user_id,
        "username": user.username,
        "password_hash": user.password_hash,
        "email": user.email,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "nature": user.nature,
        "role": user.role
        }
        result.append(user_data)
    return jsonify(result)

def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        "user_id": user.user_id,
        "username": user.username,
        "password_hash": user.password_hash,
        "email": user.email,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "nature": user.nature,
        "role": user.role
    }
    return jsonify(user_data)


def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    new_username = data.get('username', user.username)
    new_password = data.get('password', user.password_hash)  # Keep the existing password if not provided
    new_email = data.get('email', user.email)
    new_first_name = data.get('firstName', user.firstName)
    new_last_name = data.get('lastName', user.lastName)
    new_nature = data.get('nature', user.nature)
    new_role = data.get('role', user.role)


    # Vérifier si le nouvel e-mail existe déjà pour un autre utilisateur
    existing_user_with_email = User.query.filter(User.email == new_email, User.user_id != user_id).first()
    if existing_user_with_email:
        return jsonify({'message': 'Email already exists. Please use a different email.'}), 400

    # Mettre à jour les informations de l'utilisateur
    user.username = new_username
    user.email = new_email
    user.firstName = new_first_name
    user.lastName = new_last_name
    user.nature = new_nature
    user.role = new_role
    
     # Si un nouveau mot de passe est fourni, hasher et mettre à jour le mot de passe
    if new_password:
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

    db.session.commit()

    return jsonify({'message': 'User updated successfully'})


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})

