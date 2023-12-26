
# app/__init__.py

from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required, unset_jwt_cookies


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sciverse'

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view

jwt = JWTManager(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:sciversebdd@127.0.0.1:3306/sciverse' 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:sciverse2023@127.0.0.1:3306/sciverse'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sciversedb.db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate()
# Initialize Flask-Migrate
migrate.init_app(app, db)



# # MySQL Connector initialization
# mysql_connection = mysql.connector.connect(
#     host="127.0.0.1",
#     user="root",
#     password="@sciverse2023@",
#     database="sciverse",
#     port=3306
# )

# Create a cursor for executing SQL queries
# mysql_cursor = mysql_connection.cursor()


# Import routes and controllers
from app.controllers import user_controller, article_controller
from app import routes  # Import at the end to avoid circular import