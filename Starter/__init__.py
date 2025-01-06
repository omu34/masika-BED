# import os
# import time
# import psycopg2
# import threading
# from os import path
# from flask import Flask
# from config import Config
# from flask_mail import Mail
# from flask_cors import CORS
# from flask_socketio import SocketIO
# from flask_login import LoginManager
# from flask_sqlalchemy import SQLAlchemy
# from authlib.integrations.flask_client import OAuth
# from sqlalchemy import create_engine
# from app.celery_utils import make_celery


# socketio = SocketIO()
# login_manager = LoginManager()
# db = SQLAlchemy()
# oauth = OAuth()
# mail = Mail()
# cors = CORS()

# @login_manager.user_loader
# def load_user(user_id):
#     """_summary_"""
#     from starter.models import User
#     # Query the database to load the user with the given user_id
#     return User.query.get(int(user_id))


# def start_notification_listener():
#     def listen_for_notifications():
#         while True:
#             try:
#                 # Establish a dedicated connection
#                 conn = psycopg2.connect(
#                     dbname=os.getenv('DB_NAME'),
#                     user=os.getenv('DB_USER'),
#                     password=os.getenv('DB_PASSWORD'),
#                     host=os.getenv('DB_HOST'),
#                     port=os.getenv('DB_PORT')
#                 )
#                 conn.set_isolation_level(
#                     psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

#                 with conn.cursor() as cursor:
#                     cursor.execute("LISTEN featured_articles;")
#                     print(
#                         "Waiting for notifications on the 'featured_articles' channel...")
#                     while True:
#                         conn.poll()
#                         while conn.notifies:
#                             notify = conn.notifies.pop(0)
#                             print(f"Got notification: {notify.payload}")
#                             socketio.emit('featured_articles',
#                                           notify.payload, broadcast=True)

#             except psycopg2.OperationalError as e:
#                 print(f"Database connection error: {e}. Retrying in 5 seconds...")
#                 time.sleep(5)  # Retry connection after a delay

#             except Exception as e:
#                 print(f"Unexpected error in notification listener: {e}")
#                 break  # Exit the thread in case of unexpected errors

#             finally:
#                 if 'conn' in locals() and conn:
#                     conn.close()
#                     print("Notification listener connection closed.")

#     # Start the listener in a new daemon thread
#     listener_thread = threading.Thread(
#         target=listen_for_notifications, daemon=True)
#     listener_thread.start()


# def create_app():
#     """"Create and configure an instance of the Flask application."""
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Recommended approach
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     # app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
#     # app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

#     celery = make_celery(app)
#     db.init_app(app)
#     login_manager.init_app(app)
#     mail.init_app(app)
#     oauth.init_app(app)
#     cors.init_app(app)

#     # Initialize extensions
#     # Add CORS origins as needed
#     socketio.init_app(app, cors_allowed_origins="*")

#     login_manager.login_view = 'auth.auth_login'

#     # Example configuration in Flask app
#     UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
#     app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#     app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
#     app.config['MAX_CONTENT_LENGTH'] = 16 * 500 * 500

#     if not path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])

#     try:
#         with app.app_context():
#             db.engine.execute('SELECT 1')
#         print("Connection successful!")
#     except Exception as e:
#         print(f"Connection failed: {e}")


#     try:
#         from .views import views
#         app.register_blueprint(views, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing views blueprint: {e}")

#     try:
#         from .articles import articles
#         app.register_blueprint(articles, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing articles blueprint: {e}")


#     try:
#         from .auth import auth
#         app.register_blueprint(auth, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing auth blueprint: {e}")

#     try:
#         from .models import models
#         app.register_blueprint(models, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing models blueprint: {e}")

#     try:
#         from .pages import pages
#         app.register_blueprint(pages, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing pages blueprint: {e}")

#     try:
#         from .googles import googles
#         app.register_blueprint(googles, url_prefix="/")
#     except ImportError as e:
#         app.logger.error(f"Error importing googles blueprint: {e}")


#     google = oauth.register(
#         name='google',
#         client_id=os.getenv('GOOGLE_CLIENT_ID'),
#         client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
#         access_token_url='https://oauth2.googlestarters.com/token',
#         authorize_url='https://accounts.google.com/o/oauth2/auth',
#         scope='openid profile email'
#     )

#     with app.app_context():
#         db.create_all()
#     with app.app_context():
#         start_notification_listener()


#     return app,celery


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

# Extensions
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
db = SQLAlchemy()
oauth = OAuth()
mail = Mail()
cors = CORS()

# Load user callback for Flask-Login


@login_manager.user_loader
def load_user(user_id):
    """Loads user by ID for Flask-Login."""
    from starter.models import User
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

    login_manager.login_view = 'auth.auth_login'

    # File upload configuration
    app.config['UPLOAD_FOLDER'] = path.join(os.getcwd(), 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = { 'webp', 'svg','png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'svg', 'webp', 'wav', 'ogg', 'mp3'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

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
        ("starter.views", "views"),
        ("starter.articles", "articles"),
        ("starter.auth", "auth"),
        ("starter.models", "models"),
        ("starter.pages", "pages"),
        ("starter.googles", "googles"),
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
