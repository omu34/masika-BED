import os

from flask_mail import Message
from . import mail
import psycopg2.extras
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

# Secret code for admin registration
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')
SESSION_PERMANENT = os.getenv('SESSION_PERMANENT')


def get_db_connection():
    """Get a connection to the database"""
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


@auth.route('/auth_register', methods=['GET', 'POST'])
def auth_register():
    """handles user registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = request.form.get('is_admin', False)  # Checkbox value
        # Get admin code if provided
        admin_code = request.form.get('admin_code', None)

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Check if email already exists
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already exists!')
            cur.close()
            conn.close()
            return redirect(url_for('auth.auth_register'))

        # Handle admin registration
        if is_admin:  # If admin checkbox was checked
            if admin_code != ADMIN_SECRET_CODE:
                flash('Invalid admin registration code!')
                cur.close()
                conn.close()
                return redirect(url_for('auth.auth_register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user (admin or normal)
        try:
            cur.execute('''
                INSERT INTO users (username, email, password, is_admin)
                VALUES (%s, %s, %s, %s)
            ''', (username, email, hashed_password, is_admin))

            conn.commit()

            # Send confirmation email
            msg = Message('Account creation successful', recipients=[email])
            msg.body = f'Thank you for registering with Masika and Koross Advocates, {username}!'
            mail.send(msg)

            # Notify superadmin if necessary
            if is_admin:
                admin_msg = Message('New Admin Registration',
                                    recipients=[SUPER_ADMIN_EMAIL])
                admin_msg.body = f'New Admin registered: {username} ({email})'
                mail.send(admin_msg)
            flash('You are ready to go! You can now log in.')
            return redirect(url_for('auth.auth_login'))

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}')

        finally:
            cur.close()
            conn.close()

    return render_template('user_register.html')


@auth.route('/auth_login', methods=['GET', 'POST'])
def auth_login():
    """handles user login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Ensure both email and password are provided
        if not email or not password:
            flash('Please enter both email and password')
            return redirect(url_for('auth.auth_login'))

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            # Query the user based on email
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cur.fetchone()

            # Check if the user exists and if the password is correct
            if user and check_password_hash(user['password'], password):
                session['loggedin'] = True
                session['id'] = user['id']
                session['email'] = user['email']
                # Store if the user is an admin
                session['is_admin'] = user['is_admin']
                session.permanent = True  # Make the session permanent
                if user['is_admin']:  # Admin login
                    flash('Admin Login successful!')
                    return redirect(url_for('auth.admin_dashboard'))

                flash('Login successful!')

                # Send email notification to the user
                msg = Message('Login Notification', recipients=[user['email']])
                msg.body = f'You have successfully logged in, {user["email"]}!'
                mail.send(msg)

                # Notify super-admin about the login
                admin_msg = Message('User Logged In', recipients=[
                                    SUPER_ADMIN_EMAIL])
                admin_msg.body = f'User {user["email"]} has logged in.'
                mail.send(admin_msg)

                # Redirect to the home page after successful login
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect email or password')

        except Exception as e:
            flash(f'Error: {str(e)}')

        finally:
            cur.close()
            conn.close()
    return render_template('user_login.html')


@auth.route('/auth_logout', methods=['GET', 'POST'])
def auth_logout():
    """handles user logout"""
    try:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('email', None)
        flash('You have been logged out.')
        return redirect(url_for('auth.login'))
    except Exception:
        # flash('An error occurred during logout.')
        return redirect(url_for('auth.auth_login'))

# Admin


@auth.route('/admin_dashboard')
def admin_dashboard():
    """handles admin dashboard"""
    if session.get('loggedin') and session.get('is_admin'):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Fetch all users from the database
        cur.execute("SELECT * FROM users")
        users_list = cur.fetchall()

        # Fetch all messages from the database
        cur.execute("SELECT * FROM messages")
        list_messages = cur.fetchall()

        # Fetch all subscribers from the database
        cur.execute("SELECT * FROM subscribers")
        list_subscribers = cur.fetchall()

        # Fetch all articles from the database
        cur.execute("SELECT * FROM featured_articles")
        list_articles = cur.fetchall()

        cur.close()
        conn.close()

        # Pass both users_list and list_messages to the template
        return render_template('admin_dashboard.html', users_list=users_list, list_messages=list_messages, list_articles=list_articles, list_subscribers=list_subscribers)
    else:
        flash('Unauthorized access!')
        return redirect(url_for('views.home'))


# users
@auth.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """handles edit user"""
    if session.get('loggedin') and session.get('is_admin'):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            # Get form data
            username = request.form['username']
            email = request.form['email']
            is_admin = request.form.get('is_admin', False)

            # Update the user in the database
            cur.execute("UPDATE users SET username = %s, email = %s, is_admin = %s WHERE id = %s",
                        (username, email, is_admin, id))
            conn.commit()

            flash('User updated successfully!')
            return redirect(url_for('auth.admin_dashboard'))

        # If GET request, fetch the user details
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        return render_template('user_edit.html', user=user)
    else:
        flash('Unauthorized access!')
        return redirect(url_for('views.home'))


@auth.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    """handles delete user"""
    print(f"Attempting to delete user with ID: {id}")

    if session.get('loggedin') and session.get('is_admin'):
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete the user from the database
        cur.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit()

        cur.close()
        conn.close()

        flash('User deleted successfully!')
        return redirect(url_for('auth.admin_dashboard'))
    else:
        flash('Unauthorized access!')
        return redirect(url_for('views.home'))
