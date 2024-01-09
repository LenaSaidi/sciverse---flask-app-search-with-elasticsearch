from flask import Flask, request, jsonify
from flask_jwt_extended import current_user, get_jwt_identity
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from app.models import *

@jwt_required()
def add_to_favorites(article_id):
    # Check if the article is not already in favorites
    current_user_id = get_jwt_identity()
    if not FavoriteArticle.query.filter_by(user_id=current_user_id, article_id=article_id).first():
        fav_article = FavoriteArticle(user_id=current_user_id, article_id=article_id)
        db.session.add(fav_article)
        db.session.commit()

    return jsonify({'message': 'Article added to favorites successfully'})


@jwt_required()
def remove_from_favorites(article_id):
    current_user_id = get_jwt_identity()
    fav_article = FavoriteArticle.query.filter_by(user_id=current_user_id, article_id=article_id).first()

    if fav_article:
        db.session.delete(fav_article)
        db.session.commit()

    return jsonify({'message': 'Article removed from favorites successfully'})

# Function to get favorite articles
@jwt_required()
def get_favorite_articles():
    current_user_id = get_jwt_identity()
    favorite_articles = FavoriteArticle.query.filter_by(user_id=current_user_id).all()
    
    # Extract article details 
    articles = [
        {
            'id': fav.article_id,
        }
        for fav in favorite_articles
    ]

    return jsonify({'favorite_articles': articles})