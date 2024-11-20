# server.py

import os
import datetime
from flask import Blueprint, render_template
from werkzeug.utils import secure_filename
from flask_socketio import emit
from Starter import socketio

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
        "description": "Discover our strategic approach to complex commercial and corporate disputes...",
        "read_time": "6 min read",
        "image_url": "https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Corporate-Commercial.jpg",
        "url": "#",
        "url_text": "Read More",
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "youtube_id": None
    },

    {
        "title": "This is how we secured our client home",
        "description": "Witness the journey of securing a dream home...",
        "read_time": "6 min read",
        "image_url": "/static/images/home.jpg",
        "url": "#",
        "url_text": "Read More",
        "updated_at": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "youtube_id": None
    }



]

articles = Blueprint('articles', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_image_upload(file, upload_folder='static/uploads'):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return f'/static/uploads/{filename}'
    return None

# Route to render the homepage with featured articles


@articles.route("/")
def client():
    return render_template('home.html', featured_articles=featured_articles[-3:])

# Route to handle new articles with real-time updates


@socketio.on('feature_article')
def feature_article(data):
    youtube_id = get_youtube_id(data['url'])
    image_url = data['image_url']

    # Save uploaded image if provided
    if 'image' in data:
        file = data['image']
        image_url = handle_image_upload(file)

    # Add new article to featured_articles list
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
    featured_articles.append(article)

    # Emit updated list of the last 3 articles to all connected clients
    emit('update_articles', featured_articles[-3:], broadcast=True)

# Helper function to extract YouTube video ID from a URL


def get_youtube_id(url):
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            return url.split("/")[-1]
    return None
