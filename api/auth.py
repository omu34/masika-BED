from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .tasks import send_email
from . import execute_query
import os

auth = Blueprint('auth', __name__)

# Secret code for admin registration
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')

@auth.route('/auth_register', methods=['GET', 'POST'])
def auth_register():
    """Handles user registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = request.form.get('is_admin', False)
        admin_code = request.form.get('admin_code', None)

        # Check if email already exists
        existing_user = execute_query(
            'SELECT * FROM users WHERE email = %s', (email,), fetchone=True)
        if existing_user:
            flash('Email already exists!')
            return redirect(url_for('auth.auth_register'))

        # Handle admin registration
        if is_admin and admin_code != ADMIN_SECRET_CODE:
            flash('Invalid admin registration code!')
            return redirect(url_for('auth.auth_register'))

        hashed_password = generate_password_hash(password)

        # Insert new user
        execute_query(
            '''
            INSERT INTO users (username, email, password, is_admin)
            VALUES (%s, %s, %s, %s)
            ''', (username, email, hashed_password, is_admin)
        )

        # Send confirmation email
        send_email(
            'Account creation successful',
            [email],
            f'Thank you for registering with Masika and Koross Advocates, {username}!'
        )

        # Notify super-admin if necessary
        if is_admin:
            send_email(
                'New Admin Registration',
                [SUPER_ADMIN_EMAIL],
                f'New Admin registered: {username} ({email})'
            )
        flash('You are ready to go! You can now log in.')
        return redirect(url_for('auth.auth_login'))

    return render_template('user_register.html')


@auth.route('/auth_login', methods=['GET', 'POST'])
def auth_login():
    """Handles user login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both email and password')
            return redirect(url_for('auth.auth_login'))

        user = execute_query('SELECT * FROM users WHERE email = %s', (email,), fetchone=True)
        if user and check_password_hash(user['password'], password):
            session.update({
                'loggedin': True,
                'id': user['id'],
                'email': user['email'],
                'is_admin': user['is_admin']
            })
            session.permanent = True

            # Send notifications
            send_email(
                'Login Notification',
                [user['email']],
                f'You have successfully logged in, {user["email"]}!'
            )
            send_email(
                'User Logged In',
                [SUPER_ADMIN_EMAIL],
                f'User {user["email"]} has logged in.'
            )

            if user['is_admin']:
                flash('Admin Login successful!')
                return redirect(url_for('auth.admin_dashboard'))

            flash('Login successful!')
            return redirect(url_for('views.home'))

        flash('Incorrect email or password')
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


@auth.route('/admin_dashboard')
def admin_dashboard():
    """handles admin dashboard"""
    if session.get('loggedin') and session.get('is_admin'):
        # Fetch all users from the database
        users_list = execute_query("SELECT * FROM users", fetchall=True)

        # Fetch all messages from the database
        list_messages = execute_query("SELECT * FROM messages", fetchall=True)

        # Fetch all subscribers from the database
        list_subscribers = execute_query("SELECT * FROM subscribers", fetchall=True)

        # Fetch all articles from the database
        list_articles = execute_query("SELECT * FROM featured_articles", fetchall=True)

        # Pass both users_list and list_messages to the template
        return render_template('admin_dashboard.html', users_list=users_list, list_messages=list_messages, list_articles=list_articles, list_subscribers=list_subscribers)
    else:
        flash('Unauthorized access!')
        return redirect(url_for('views.add_message'))

# Optimized Edit User


@auth.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """Handles editing a user"""
    if not (session.get('loggedin') and session.get('is_admin')):
        flash('Unauthorized access!')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        is_admin = request.form.get('is_admin', False)

        # Update the user in the database
        execute_query(
            """
            UPDATE users
            SET username = %s, email = %s, is_admin = %s
            WHERE id = %s
            """,
            (username, email, is_admin, id)
        )

        flash('User updated successfully!')
        return redirect(url_for('auth.admin_dashboard'))

    # Fetch user details for GET request
    user = execute_query(
        "SELECT * FROM users WHERE id = %s", (id,), fetchone=True
    )
    return render_template('user_edit.html', user=user)


# Optimized Delete User
@auth.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    """Handles deleting a user"""
    if not (session.get('loggedin') and session.get('is_admin')):
        flash('Unauthorized access!')
        return redirect(url_for('views.home'))

    # Delete the user from the database
    execute_query("DELETE FROM users WHERE id = %s", (id,))
    flash('User deleted successfully!')
    return redirect(url_for('auth.admin_dashboard'))
