from flask import Blueprint, flash
from werkzeug.security import check_password_hash, generate_password_hash

from Starter import db

models = Blueprint('models', __name__)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.is_admin = is_admin
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    # Flask-Login requires `get_id` to retrieve the user's ID.
    def get_id(self):
        return self.id  

    def __repr__(self):
        return f'<User {self.username}>'
    
class AboutUs(db.Model):
    __tablename__ = 'aboutUs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    
    
    
def create_user(username, email, password, is_admin=False):
    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        flash(f'User with username "{username}" already exists!')
        return None  # Or handle it in another way (e.g., update user info)

    # If the user doesn't exist, create a new user
    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password, method='scrypt'),
        is_admin=is_admin
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user



