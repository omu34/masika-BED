import os
import time
from flask import Blueprint, current_app, request, jsonify, render_template, send_from_directory
from flask_socketio import emit
from werkzeug.utils import secure_filename
from .models import db, FeaturedArticle
from . import socketio
from .tasks import allowed_file, save_file, validate_article_data

articles = Blueprint('articles', __name__)

VALID_ARTICLE_TYPES = ["news", "videos", "gallery"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'svg', 'webp', 'wav', 'ogg', 'mp3' }


@articles.route('/articles', methods=['POST'])
def upload_article():
    try:
        # Get form data
        title = request.form['title']
        description = request.form['description']
        article_type = request.form['article_type']
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

        # Add article to the database
        article_id = len(articles) + 1
        article = {
            'id': article_id,
            'title': title,
            'description': description,
            'type': article_type,
            'file': filename,  # Save only filename, not full path
            'is_featured': False,
        }
        articles.append(article)

        return jsonify({'message': 'Article uploaded successfully', 'article': article}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
# Directing saves to client


@articles.route('/blog')
def blog():
    """Render the homepage."""
    return render_template('blog.html')

# Socket.IO event for client connection
@socketio.on('connect')
def handle_connect():
    """Send the latest two articles of each type to the client."""
    featured_articles = {}
    for article_type in VALID_ARTICLE_TYPES:
        articles = (
            FeaturedArticle.query.filter_by(type=article_type)
            .order_by(FeaturedArticle.id.desc())
            .limit(2)  # Fetch only the last 2 articles
            .all()
        )
        featured_articles[article_type] = [
            {
                "id": article.id,
                "title": article.title,
                "description": article.description,
                "link": article.link,
                "time_featured": article.time_featured,
                "time_to_read": article.time_to_read,
                "is_featured": article.is_featured,
            }
            for article in articles
        ]
    emit('initial_data', featured_articles)


@articles.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    """Serve uploaded files."""
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if os.path.exists(os.path.join(upload_path, filename)):
        return send_from_directory(upload_path, filename)

    return "File not found", 404

# Update Articles
@articles.route('/articles/update-article/<article_type>', methods=['POST'])
def update_article(article_type):
    """Add or update an article."""
    if article_type not in VALID_ARTICLE_TYPES:
        return jsonify({"error": "Invalid article type"}), 400

    title = request.form.get('title')
    description = request.form.get('description')
    time_to_read = request.form.get('time_to_read', "N/A")
    link = request.form.get('link')
    file = request.files.get('file')

    # Validate data
    error = validate_article_data(title, description, time_to_read)
    if error:
        return jsonify({"error": error}), 400

    # Handle file upload or link
    file_url = save_file(file, article_type) if file else link

    # Create and save the article
    article = FeaturedArticle(
        type=article_type,
        title=title,
        description=description,
        link=file_url,
        time_featured=time.strftime('%Y-%m-%d %H:%M:%S'),
        time_to_read=time_to_read,
        is_featured=False,
    )
    db.session.add(article)
    db.session.commit()

    # Notify all clients
    socketio.emit('update_featured', {
        "type": article_type,
        "data": {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "link": article.link,
            "time_featured": article.time_featured,
            "time_to_read": article.time_to_read,
            "is_featured": article.is_featured,
        }
    })
    return jsonify({"message": f"Article added to {article_type}!"}), 200

# Toggling Articles


@articles.route('/articles/toggle-featured/<article_type>/<int:article_id>', methods=['POST'])
def toggle_featured(article_type, article_id):
    """Toggle the 'featured' status of an article."""
    if article_type not in VALID_ARTICLE_TYPES:
        return jsonify({"error": "Invalid article type"}), 400

    article = FeaturedArticle.query.filter_by(
        id=article_id, type=article_type).first()
    if not article:
        return jsonify({"error": "Article not found"}), 404

    data = request.json
    is_featured = data.get('isFeatured', False)
    article.is_featured = is_featured
    db.session.commit()

    # Notify all clients
    socketio.emit('update_featured', {
        "type": article_type,
        "data": {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "link": article.link,
            "time_featured": article.time_featured,
            "time_to_read": article.time_to_read,
            "is_featured": article.is_featured,
        }
    })
    return jsonify({"message": "Feature status updated!"}), 200

# Delete Articles


@articles.route('/articles/delete-article/<article_type>/<int:article_id>', methods=['DELETE'])
def delete_article(article_type, article_id):
    """Delete an article."""
    if article_type not in VALID_ARTICLE_TYPES:
        return jsonify({"error": "Invalid article type"}), 400

    article = FeaturedArticle.query.filter_by(
        id=article_id, type=article_type).first()
    if not article:
        return jsonify({"error": "Article not found"}), 404

    db.session.delete(article)
    db.session.commit()

    # Notify all clients
    articles = (
        FeaturedArticle.query.filter_by(type=article_type)
        .order_by(FeaturedArticle.id.desc())
        .all()
    )
    serialized_articles = [
        {
            "id": art.id,
            "title": art.title,
            "description": art.description,
            "link": art.link,
            "time_featured": art.time_featured,
            "time_to_read": art.time_to_read,
            "is_featured": art.is_featured,
        }
        for art in articles
    ]
    socketio.emit('initial_data', {article_type: serialized_articles})
    return jsonify({"message": "Article deleted successfully!"}), 200
