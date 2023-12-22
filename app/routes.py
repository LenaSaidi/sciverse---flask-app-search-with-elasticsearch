# app/routes.py

from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.models import User
from app.controllers import user_controller
from app.controllers import auth_controller
from app.controllers import moderator_controller
from app.controllers import admin_controller

# auth related routes
app.add_url_rule('/signup', 'signup', auth_controller.signup, methods=['POST'])
app.add_url_rule('/signin', 'signin', auth_controller.signin, methods=['POST'])
app.add_url_rule('/signout', 'signout', auth_controller.signout, methods=['POST'])


# User-related routes
app.add_url_rule('/users', 'get_users', user_controller.get_users, methods=['GET'])
app.add_url_rule('/user/get/<int:user_id>', 'get_user', user_controller.get_user, methods=['GET'])
app.add_url_rule('/user/update/<int:user_id>', 'update_user', user_controller.update_user, methods=['PUT'])
app.add_url_rule('/user/delete/<int:user_id>', 'delete_user', user_controller.delete_user, methods=['DELETE'])

# Moderator-related routes
app.add_url_rule('/moderators', 'get_moderators', moderator_controller.get_moderators, methods=['GET'])
app.add_url_rule('/moderator/create', 'create_moderator', moderator_controller.create_moderator, methods=['POST'])

# Admin-related routes
app.add_url_rule('/admins', 'get_admins', admin_controller.get_admins, methods=['GET'])
app.add_url_rule('/admin/create', 'create_admin', admin_controller.create_admin, methods=['POST'])



if __name__ == '__main__':
    app.run(debug=True)