# init_db.py
from app import app, db

# Create the Flask application
app = app()

# Push the application context
with app.app_context():
    # Create all database tables
    db.create_all()

print("Database tables created.")
