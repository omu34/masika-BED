from flask import url_for, Blueprint, current_app, flash
from flask_mail import Message
from threading import Thread
import re
import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .models import User
from . import db  

tasks = Blueprint("tasks", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    """Save file and return its URL."""
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))
    return url_for('articles.uploaded_file', folder=folder, filename=filename, _external=True)

def send_email_async(app, msg):
    """Send email in a separate thread."""
    with app.app_context():
        try:
            mail = app.extensions['mail']
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_email(subject, recipients, body):
    """Prepare and send email asynchronously."""
    msg = Message(subject=subject, recipients=recipients, body=body)
    Thread(target=send_email_async, args=(current_app._get_current_object(), msg)).start()

def subscriber_email_to_admin(email):
    admin_email = [SUPER_ADMIN_EMAIL]
    subject = "New Subscription Received"
    body = f"You have received a new subscription:\n\nEmail: {email}"
    send_email(subject, admin_email, body)

def subscriber_email_to_client(email):
    subject = "Thank You for Subscribing"
    body = f"Hi {email},\n\nThank you for subscribing to us. We will keep you updated.\n\nBest Regards,\nMasika and Koross Advocates"
    send_email(subject, [email], body)

def send_email_to_admin(name, phone_number, email, texts):
    admin_email = [SUPER_ADMIN_EMAIL]
    subject = "New Message Received"
    body = f"You have received a new message:\n\nName: {name}\nPhone Number: {phone_number}\nEmail: {email}\nMessage: {texts}"
    send_email(subject, admin_email, body)

def send_email_to_client(name, email):
    subject = "Thank You for Contacting Us"
    body = f"Hi {name},\n\nThank you for reaching out to us. We will get back to you shortly.\n\nBest Regards,\nMasika and Koross Advocates"
    send_email(subject, [email], body)

def is_valid_email(email):
    """Validate the email format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def validate_article_data(title, description, time_to_read):
    if not title or not description:
        return "Title and description are required."
    if not time_to_read.isdigit():
        return "Time to read must be a number."
    return None

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
