import os
from flask import Blueprint, request, flash, redirect, url_for
import psycopg2.extras
from flask_mail import Message
from Starter import mail

newsletter = Blueprint("newsletter", __name__)


def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


@newsletter.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        user_email = request.form['email']  # Get the email entered by the user
        try:
            # Send an email to the user
            msg_to_user = Message(
                'Subscription Successful',
                recipients=[user_email]  # The email entered by the user
            )
            msg_to_user.body = f"Thank you for subscribing to our newsletter, {user_email}!"
            mail.send(msg_to_user)

            # Send an email to the admin
            msg_to_admin = Message(
                'New Subscription Alert',
                recipients=['bernardomuse22@gmail.com']  # Admin's email address
            )
            msg_to_admin.body = f"New subscription from: {user_email}"
            mail.send(msg_to_admin)

            flash('You have successfully subscribed to the newsletter!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('views.home'))  # Redirect to the homepage or another page
