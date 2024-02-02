# app/models.py

# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app import db

# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    nature = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), default='user')  # Default role is 'user'
    field = db.Column(db.String(50), nullable=False)
    favorite_articles = db.relationship('Article', secondary='favorite_articles', backref='users')
    

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    full_text = db.Column(db.Text, nullable=False)
    pdf_url = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    authors = db.relationship('Author', secondary='article_author', backref=db.backref('articles', lazy='dynamic'), cascade="all, delete")
    keywords = db.relationship('Keyword', secondary='article_keyword', backref=db.backref('articles', lazy='dynamic'), cascade="all, delete")
    references = db.relationship('BibliographicReference', secondary='article_reference', backref=db.backref('articles', lazy='dynamic'), cascade="all, delete")
    article_edits = db.relationship('ArticleEdit', backref='article', lazy='dynamic', cascade="all, delete")
    article_elasticsearch_mapping = db.relationship('ArticleElasticsearchMapping', backref='article', lazy='dynamic', cascade="all, delete")

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    institutions = db.relationship('Institution', secondary='author_institution', backref=db.backref('authors', lazy='dynamic'))

class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(255), unique=False, nullable=False)

class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)

class BibliographicReference(db.Model):
    __tablename__ = 'bibliographic_references'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    reference = db.Column(db.String(1000))
# Junction Tables

class AuthorInstitution(db.Model):
    __tablename__ = 'author_institution'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'))

class ArticleAuthor(db.Model):
    __tablename__ = 'article_author'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

class ArticleKeyword(db.Model):
    __tablename__ = 'article_keyword'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'))

class ArticleReference(db.Model):
    __tablename__ = 'article_reference'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    reference_id = db.Column(db.Integer, db.ForeignKey('bibliographic_references.id'))

class FavoriteArticle(db.Model):
    __tablename__ = 'favorite_articles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

class ArticleEdit(db.Model):
    __tablename__ = 'article_edits'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)

    # edited_text = db.Column(db.Text)

class ArticleElasticsearchMapping(db.Model):
    __tablename__ = 'article_elasticsearch_mapping'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False) 
    elasticsearch_id = db.Column(db.String(255), nullable=False)   


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))