from flask import Blueprint, flash
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from datetime import datetime

models = Blueprint('models', __name__)

# User Model
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

    def get_id(self):
        return self.id  # Required for Flask-Login

    def __repr__(self):
        return f'<User {self.username}>'


# About Us Model
class AboutUs(db.Model):
    __tablename__ = 'aboutUs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<AboutUs {self.title}>"
    
    # Featured Article


class FeaturedArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # "news", "videos", "gallery"
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    time_featured = db.Column(db.String(50), nullable=False)
    time_to_read = db.Column(db.String(20), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    youtube_id = db.Column(db.String(20))
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return f"<FeaturedArticle {self.title}>"
class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Subscriber {self.id} - {self.name}>'

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    texts = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id} - {self.name}>'
















