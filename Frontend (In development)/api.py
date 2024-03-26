from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.username

# Create tables
db.create_all()

def get_session_history_file(username):
    """
    Get the path to the session history file for a given username.

    Args:
        username (str): The username of the user.

    Returns:
        str or None: The path to the session history file if it exists, None otherwise.
    """
    session_history_dir = 'session_history'
    if not os.path.exists(session_history_dir):
        os.makedirs(session_history_dir)

    session_history_file = os.path.join(session_history_dir, f"{username}_session_history.txt")
    if os.path.exists(session_history_file):
        return session_history_file
    else:
        return None

# API endpoints
@app.route('/signup', methods=['POST'])
def signup():
    """
    Sign up a new user.

    Creates a new user in the database.

    Returns:
        jsonify: A JSON response with a success message or an error message.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    institution = data.get('institution')

    # Validate email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Invalid email'}), 400

    # Check if email domain is allowed
    if not email.endswith('@nd.edu') and not email.endswith('@upr.edu'):
        return jsonify({'error': 'Email domain not allowed'}), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create user
    new_user = User(username=username, password=hashed_password, email=email, institution=institution)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    """
    Log in a user.

    Checks the username and password against the database.

    Returns:
        jsonify: A JSON response with a success message or an error message.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Find user by username
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Check password
    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Login successful
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)

# Werkzeug is used for password hashing and checking. It provides security features for Flask applications.
