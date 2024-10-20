import os
from dotenv import load_dotenv

# Load environment variables from the .env file
# load_dotenv()

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Loaded from environment variable
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Loaded from environment variable
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    # SQL configuration
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoid warning
    
    ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
    SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
    
