from flask import Blueprint, redirect, url_for, session, jsonify
from Starter import oauth  # Make sure to import oauth from where it's initialized

googles = Blueprint("googles", __name__)

@googles.route('/')
def homepage():
    return 'Welcome to the Google login demo! <a href="/googles/login">Login with Google</a>'

@googles.route('/google_login')
def google_login():
    google = oauth.create_client('google')  # Create Google OAuth client
    redirect_uri = url_for('googles.auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@googles.route('/auth/callback')
def auth_callback():
    google = oauth.create_client('google')  # Create Google OAuth client
    try:
        token = google.authorize_access_token()  # Retrieve access token
        user_info = google.parse_id_token(token)  # Retrieve user info
        session['user'] = user_info  # Store user info in session
        return jsonify(user_info)  # Return user info as JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return error if something goes wrong

@googles.route('/google_logout')
def google_logout():
    session.pop('user', None)  # Clear user session
    return redirect(url_for('googles.homepage'))
