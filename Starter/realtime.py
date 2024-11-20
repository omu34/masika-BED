import os
import datetime
import psycopg2
import threading
from flask import Blueprint, jsonify, request, redirect, url_for, jsonify, render_template, current_app
from .models import Page, Section, Subsection, db
from werkzeug.utils import secure_filename
from flask_socketio import emit
from Starter import socketio


realtime = Blueprint('realtime', __name__)


# Sample featured articles list (can be populated from the database or used as fallback)
featured_articles = [
    {
        "title": "Best Won Procurement Case",
        "description": "A deep dive into how we secured a procurement case...",
        "read_time": "6 min read",
        "image_url": "/static/images/procurement.jpg",
        "url": "#",
        "url_text": "Read More",
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "youtube_id": None
    }, 
    {
        "title": "How we handle commercial and corporate cases",
        "description": "Corporate disputes can be complex and require a strategic approach...",
        "read_time": "6 min read",
        "image_url": "https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Corporate-Commercial.jpg",
        "url": "#",
        "url_text": "Read More",
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "youtube_id": None
    }, 
    {
        "title": "How we secured client home",
        "description": "Client home secured successfully...",
        "read_time": "6 min read",
        "image_url": "/static/images/home.jpg",
        "url": "#",
        "url_text": "Read More",
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "youtube_id": None
    },
    
]


realtime = Blueprint('realtime', __name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

# Function to listen for notifications
def listen_for_changes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("LISTEN pages_change;")
    cursor.execute("LISTEN sections_change;")
    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            data = fetch_updated_data()
            socketio.emit('page_update', data)

# Start listening in a new thread
listener_thread = threading.Thread(target=listen_for_changes)
listener_thread.start()

# Function to fetch updated data from the database

def fetch_updated_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id AS section_id, s.title AS section_title, s.image_url AS section_image,
               ss.title AS subsection_title, ss.description, ss.image_url AS subsection_image
        FROM sections s
        LEFT JOIN subsections ss ON ss.section_id = s.id;
    """)
    sections_data = cursor.fetchall()
    structured_data = {
        'sections': [
            {
                'id': row[0],
                'title': row[1],
                'image_url': row[2],
                'subsections': [{'title': row[3], 'description': row[4], 'image_url': row[5]}]
            } for row in sections_data
        ]
    }
    cursor.close()
    conn.close()
    return structured_data

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to the server!'})
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# Helper: Check allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper: Handle image upload
def handle_image_upload(file, upload_folder='static/uploads'):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return f'/static/uploads/{filename}'
    return None




# server.py

# Route to render the homepage with featured articles
@realtime.route("/")
def client():
    return render_template('home.html', articles=featured_articles[-3:])

# Add this to server.py
@socketio.on('feature_article')
def feature_article(data):
    # Process the received data from the admin
    youtube_id = get_youtube_id(data['url'])
    image_url = data['image_url']

    # Create the new article object
    article = {
        "title": data['title'],
        "description": data['description'],
        "image_url": image_url,
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "read_time": data['read_time'],
        "url": data['url'],
        "url_text": data['url_text'],
        "youtube_id": youtube_id
    }

    # Add new article to the featured_articles list (use a persistent store like a database in production)
    featured_articles.append(article)

    # Emit updated list of the last 3 articles to all clients (admin and front-end)
    emit('update_articles', featured_articles[-3:], broadcast=True)


# Helper function to extract YouTube video ID from a URL
def get_youtube_id(url):
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            return url.split("/")[-1]
    return None




