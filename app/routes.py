# app/routes.py

from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.elasticsearch import search_article
from app.models import User
from app.controllers import user_controller
from app.controllers import auth_controller
from app.controllers import moderator_controller
from app.controllers import admin_controller
from app.controllers import article_controller
from app.controllers import favorite_controller


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

# Article-related routes
app.add_url_rule('/article/getStatic/<int:article_id>', 'get_article', article_controller.get_article, methods=['GET'])
app.add_url_rule('/article/add', 'add_article', article_controller.add_article, methods=['POST'])
app.add_url_rule('/articles', 'get_articles', article_controller.get_articles, methods=['GET'])
app.add_url_rule('/all-articles', 'get_all_articles', article_controller.get_all_articles, methods=['GET'])
app.add_url_rule('/article/edit/<int:article_id>', 'edit_article', article_controller.edit_article, methods=['PUT'])
app.add_url_rule('/article/delete/<int:article_id>', 'delete_article', article_controller.delete_article, methods=['DELETE'])
app.add_url_rule('/article/edits/<int:article_id>', 'get_article_edits', article_controller.get_article_edits, methods=['GET'])
app.add_url_rule('/search-article', 'search_article', search_article, methods=['POST'])
app.add_url_rule('/article/get/<int:article_id>', 'get_article_from_elasticsearch', article_controller.get_article_from_elasticsearch, methods=['GET'])

# Fav_articles-related routes

app.add_url_rule('/favorite_articles/get', 'get_favorite_articles', favorite_controller.get_favorite_articles, methods=['GET'])
app.add_url_rule('/favorites/add/<int:article_id>', 'add_to_favorites', favorite_controller.add_to_favorites, methods=['POST'])
app.add_url_rule('/favorites/remove/<int:article_id>', 'remove_from_favorites', favorite_controller.remove_from_favorites, methods=['DELETE'])






if __name__ == '__main__':
    app.run(debug=True)
