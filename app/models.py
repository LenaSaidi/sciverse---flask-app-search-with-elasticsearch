# app/models.py

# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    nature = db.Column(db.Text)
    role = db.Column(db.String(50), default='user')  # Default role is 'user'

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    abstract = db.Column(db.Text)
    full_text = db.Column(db.Text)
    pdf_url = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    authors = db.relationship('Author', secondary='article_author', backref=db.backref('articles', lazy='dynamic'))
    keywords = db.relationship('Keyword', secondary='article_keyword', backref=db.backref('articles', lazy='dynamic'))
    references = db.relationship('BibliographicReference', secondary='article_reference', backref=db.backref('articles', lazy='dynamic'))

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    institutions = db.relationship('Institution', secondary='author_institution', backref=db.backref('authors', lazy='dynamic'))

class Institution(db.Model):
    __tablename__ = 'institutions'
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(255), unique=False, nullable=False)

class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255))

class BibliographicReference(db.Model):
    __tablename__ = 'bibliographic_references'
    id = db.Column(db.Integer, primary_key=True)
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