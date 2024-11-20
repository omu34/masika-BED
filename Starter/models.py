from sqlalchemy.dialects.postgresql import JSONB
from flask import Blueprint, flash
from werkzeug.security import check_password_hash, generate_password_hash
from Starter import db
from datetime import datetime

models = Blueprint('models', __name__)

# Page Model
class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(JSONB, nullable=False)  # Changed to JSONB for Postgres
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    sections = db.relationship('Section', backref='page', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f"<Page {self.title}>"


# Section Model
class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Subsections
    subsections = db.relationship('Subsection', backref='section', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"<Section {self.title}>"


# Subsection Model
class Subsection(db.Model):
    __tablename__ = 'subsections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Subsection {self.title}>"


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
    __tablename__ = 'featured_articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    url = db.Column(db.String(255))
    url_text = db.Column(db.String(50), default='Read More')
    read_time = db.Column(db.String(50))
    youtube_id = db.Column(db.String(20))
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FeaturedArticle {self.title}>"


# Function to Create User
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











