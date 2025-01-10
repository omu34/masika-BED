# import os
# from dotenv import load_dotenv
# # Load environment variables from .env file
# basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

# class Config:
#     # Mail configuration
#     MAIL_SERVER = 'smtp.gmail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = os.getenv('MAIL_USERNAME')  
#     MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  
#     MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
#     # OAuth configuration
#     GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
#     GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
#     # SQL configuration
#     SECRET_KEY = os.urandom(24)    
#     ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
#     SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')
#     SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
#     SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
#     #PostgreSQL configuration    
#     user=os.getenv('DB_USER'),
#     host = os.getenv('DB_HOST'),
#     port = os.getenv('DB_PORT'),
#     dbname = os.getenv('DB_NAME'),
#     password=os.getenv('DB_PASSWORD'),

import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # General settings
    # Default to a random key for security
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SESSION_PERMANENT = os.getenv(
        'SESSION_PERMANENT', 'True').lower() == 'true'

    # File upload configuration
    # Save uploaded files to 'uploads' folder
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'webp', 'svg', 'png', 'jpg', 'jpeg', 'gif', 'mp4',
                          'webm', 'ogg', 'wav', 'mp3'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maximum file size: 16 MB

    # Mail configuration
    # Default to Gmail SMTP
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    # SQL configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv(
        'SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'

    # Admin configuration
    ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
    SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')

    # Celery configuration
    CELERY_BROKER_URL = os.getenv(
        'CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv(
        'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # PostgreSQL configuration (for raw usage if needed)
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')  # Default to localhost
    DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Environment-specific configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
