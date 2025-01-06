import os
from dotenv import load_dotenv
# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    # OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    # SQL configuration
    SECRET_KEY = os.urandom(24)    
    ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
    SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    #PostgreSQL configuration    
    user=os.getenv('DB_USER'),
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    dbname = os.getenv('DB_NAME'),
    password=os.getenv('DB_PASSWORD'),
    
    
