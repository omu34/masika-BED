import os
import time
import psycopg2
import threading
from os import path
from flask import Flask
from config import Config
from flask_mail import Mail
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from sqlalchemy.sql import text
from celery import Celery
import sys
print(sys.path)

# Extensions
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
db = SQLAlchemy()
oauth = OAuth()
mail = Mail()
cors = CORS()
celery = Celery()
# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Loads user by ID for Flask-Login."""
    from api.models import User
    return User.query.get(int(user_id))

# Notification Listener
def start_notification_listener():
    """Starts a PostgreSQL LISTEN/NOTIFY listener in a separate thread."""
    def listen_for_notifications():
        while True:
            try:
                # Establish a dedicated PostgreSQL connection
                conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    host=os.getenv('DB_HOST'),
                    port=os.getenv('DB_PORT')
                )
                conn.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

                with conn.cursor() as cursor:
                    cursor.execute("LISTEN featured_articles;")
                    print(
                        "Listening for notifications on 'featured_articles' channel...")

                    while True:
                        conn.poll()
                        while conn.notifies:
                            notify = conn.notifies.pop(0)
                            print(f"Received notification: {notify.payload}")
                            socketio.emit('featured_articles',
                                          notify.payload, broadcast=True)

            except psycopg2.OperationalError as e:
                print(f"Database connection error: {e}. Retrying in 5 seconds...")
                time.sleep(5)  # Retry after delay

            except Exception as e:
                print(f"Unexpected error: {e}")
                break  # Exit the thread on critical failure

            finally:
                if 'conn' in locals() and conn:
                    conn.close()
                    print("Closed notification listener connection.")

    # Start listener in a daemon thread
    threading.Thread(target=listen_for_notifications, daemon=True).start()

# Db Connection

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


# Helper function to execute a database query

def execute_query(query, params=(), fetchone=False, fetchall=False):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params)
                conn.commit()

                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        return None

# Flask Application Factory

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)
    celery.conf.update(app.config)
    login_manager.login_view = 'auth.auth_login'

    # File upload configuration
    app.config['UPLOAD_FOLDER'] = path.join(os.getcwd(), 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = { 'webp', 'svg','png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'svg', 'webp', 'wav', 'ogg', 'mp3'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    if not path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Test database connection
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    # Register blueprints
    blueprints = [
        ("api.views", "views"),
        ("api.articles", "articles"),
        ("api.auth", "auth"),
        ("api.models", "models"),
        ("api.pages", "pages"),
        ("api.googles", "googles"),
        ("api.tasks", "tasks"),
    ]

    for module_path, blueprint_name in blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            app.register_blueprint(
                getattr(module, blueprint_name), url_prefix="/")
        except ImportError as e:
            app.logger.error(f"Error importing blueprint '{blueprint_name}': {e}")

    # OAuth configuration
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://oauth2.googlestarters.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        scope='openid profile email'
    )

    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    return app
