from . import mail, get_db_connection
from flask_mail import Message
from flask import redirect, url_for, flash, request, Blueprint, current_app, send_from_directory
from threading import Thread
import re
import psycopg2
import os
import psycopg2.extras
from werkzeug.utils import secure_filename

tasks = Blueprint("tasks", __name__)

# Define allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper function to validate article data


def validate_article_data(title, description, time_to_read):
    """Validate article data before adding."""
    if not title or not description:
        return "Title and description are required."
    if time_to_read and not time_to_read.isdigit():
        return "Time to read must be a numeric value."
    return None

# Save uploaded files


def save_file(file, folder):
    """Save file and return its URL."""
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))
    return url_for('articles.uploaded_file', folder=folder, filename=filename, _external=True)

# Send email asynchronously

def send_email_async(app, msg):
    """Sends email in a separate thread to avoid delays."""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")


def send_email(subject, recipients, body):
    """Helper function to prepare and send an email asynchronously."""
    msg = Message(subject=subject, recipients=recipients, body=body)
    Thread(target=send_email_async, args=(mail._app, msg)).start()

# Updated subscriber_email_to_admin

def subscriber_email_to_admin(email):
    admin_email = "bernardomuse22@gmail.com"
    subject = "New Subscription Received"
    body = f"""
    You have received a new subscription:
    Email: {email}
    """
    send_email(subject, [admin_email], body)

# Updated subscriber_email_to_client
def subscriber_email_to_client(email):
    subject = "Thank You for Subscribing"
    body = f"""
    Hi {email},

    Thank you for subscribing to us. We have received your subscription and will keep you updated.

    Best Regards,
    Masika and Koross Advocates
    """
    send_email(subject, [email], body)

# Updated send_email_to_admin
def send_email_to_admin(name, phone_number, email, texts):
    admin_email = "skmasika@gmail.com"
    subject = "New Message Received"
    body = f"""
    You have received a new message:
    Name: {name}
    Phone Number: {phone_number}
    Email: {email}
    Message: {texts}
    """
    send_email(subject, [admin_email], body)

# Updated send_email_to_client


def send_email_to_client(name, email):
    subject = "Thank You for Contacting Us"
    body = f"""
    Hi {name},

    Thank you for reaching out to us. We have received your message and will get back to you shortly.

    Best Regards,
    Masika and Koross Advocates
    """
    send_email(subject, [email], body)

def is_valid_email(email):
    """Validate the email format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None



