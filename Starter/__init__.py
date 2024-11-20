import os
import psycopg2
import threading
import time
import select
from os import path
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config

socketio = SocketIO()
login_manager = LoginManager()
db = SQLAlchemy()
oauth = OAuth()
mail = Mail()
cors = CORS()


@login_manager.user_loader
def load_user(user_id):
    """_summary_"""
    from Starter.models import User
    # Query the database to load the user with the given user_id
    return User.query.get(int(user_id))

def start_notification_listener():
    try:
        # Connect to PostgreSQL (consider using app config for credentials)
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        def listen_for_notifications(conn):
            try:
                with conn.cursor() as cursor:  # Ensure the cursor is created within this context
                    cursor.execute("LISTEN article_update;")
                    print("Waiting for notifications on the 'article_update' channel...")

                    while True:
                        conn.poll()  # Poll the database for notifications
                        while conn.notifies:
                            notify = conn.notifies.pop(0)
                            print(f"Got notification: {notify.payload}")
                            
                            # Emit the notification payload to all connected clients via SocketIO
                            socketio.emit('article_update', notify.payload, broadcast=True)

            except psycopg2.Error as e:
                print(f"Error while listening for notifications: {e}")

        # Start a new thread for listening to PostgreSQL notifications
        listener_thread = threading.Thread(target=listen_for_notifications, args=(conn,))
        listener_thread.daemon = True  # Daemonize thread to shut it down with the app
        listener_thread.start()

    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure that the connection is closed if needed
        try:
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")
        except NameError:
            print("No connection to close.")



def create_app():
    """"Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    cors.init_app(app)
    
    login_manager.login_view = 'auth.auth_login'

    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 500 * 500

    if not path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    
    try:
        from .views import views
        app.register_blueprint(views, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing views blueprint: {e}")

    try:
        from .newsletter import newsletter
        app.register_blueprint(newsletter, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing newsletter blueprint: {e}")

    try:
        from .auth import auth
        app.register_blueprint(auth, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing auth blueprint: {e}")

    try:
        from .models import models
        app.register_blueprint(models, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing models blueprint: {e}")

    try:
        from .pages import pages
        app.register_blueprint(pages, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing pages blueprint: {e}")

    try:
        from .googles import googles
        app.register_blueprint(googles, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing googles blueprint: {e}")

    try:
        from .realtime import realtime  # type: ignore
        app.register_blueprint(realtime, url_prefix="/")
    except ImportError as e:
        app.logger.error(f"Error importing realtime blueprint: {e}")


    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        scope='openid profile email'
    )

    with app.app_context():
        db.create_all()
    with app.app_context():
        start_notification_listener()

    return app







