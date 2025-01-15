import os
import time
from flask import Blueprint, current_app, request, jsonify, render_template, send_from_directory
from flask_socketio import emit
from werkzeug.utils import secure_filename
from .models import db, FeaturedArticle
from .tasks import allowed_file, save_file, validate_article_data
from . import socketio  

blogs = Blueprint('blogs', __name__)

VALID_ARTICLE_TYPES = ["news", "videos", "gallery"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4',
                      'webm', 'ogg', 'svg', 'webp', 'wav', 'ogg', 'mp3'}


@blogs.route('/articles', methods=['POST'])
def upload_article():
    try:
        title = request.form['title']
        description = request.form['description']
        article_type = request.form['article_type']
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(
                # Include type in path
                current_app.config['UPLOAD_FOLDER'], article_type, filename)
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
        else:
            return jsonify({'error': 'Invalid file'}), 400

        article = FeaturedArticle(
            type=article_type,
            title=title,
            description=description,
            link=filename,  # Store only filename
            time_featured=time.strftime('%Y-%m-%d %H:%M:%S'),
            is_featured=False,
        )
        db.session.add(article)
        db.session.commit()

        return jsonify({'message': 'Article uploaded successfully', 'article': {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "link": article.link,
            "time_featured": article.time_featured,
            "is_featured": article.is_featured,
        }}), 201

    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({'error': str(e)}), 500  # Use 500 for server error


@blogs.route('/blog')
def blog():
    return render_template('blog.html')


@socketio.on('get_all_articles')
def handle_get_all_articles():
    """Handles the client's request for all article data (for blog page)."""
    try:
        articles = FeaturedArticle.query.order_by(
            FeaturedArticle.id.desc()).all()
        featured_articles = {}
        for article in articles:
            featured_articles.setdefault(article.type, []).append({
                "id": article.id,
                "title": article.title,
                "description": article.description,
                "link": article.link,
                "time_featured": article.time_featured,
                "time_to_read": article.time_to_read,
                "is_featured": article.is_featured,
            })
        # Changed event name to differentiate
        emit('initial_data_blog', featured_articles)
    except Exception as e:
        print(f"Error fetching initial data: {e}")
        emit('initial_data_blog', {"error": "Failed to fetch articles"})
@blogs.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    """Serve uploaded files."""
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if os.path.exists(os.path.join(upload_path, filename)):
        # Use send_from_directory directly
        return send_from_directory(upload_path, filename)

    return "File not found", 404


@blogs.route('/articles/update-article/<article_type>', methods=['POST'])
def update_article(article_type):
    if article_type not in VALID_ARTICLE_TYPES:
        return jsonify({"error": "Invalid article type"}), 400

    title = request.form.get('title')
    description = request.form.get('description')
    time_to_read = request.form.get('time_to_read', "N/A")
    link = request.form.get('link')
    file = request.files.get('file')

    error = validate_article_data(title, description, time_to_read)
    if error:
        return jsonify({"error": error}), 400

    file_url = save_file(file, article_type) if file else link

    try:
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
        # Notify all clients (same as before)
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@blogs.route('/articles/toggle-featured/<article_type>/<int:article_id>', methods=['POST'])
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

    pass


@blogs.route('/articles/delete-article/<article_type>/<int:article_id>', methods=['DELETE'])
def delete_article(article_type, article_id):
    if article_type not in VALID_ARTICLE_TYPES:
        return jsonify({"error": "Invalid article type"}), 400

    try:
        article = FeaturedArticle.query.filter_by(
            id=article_id, type=article_type).first()
        if not article:
            return jsonify({"error": "Article not found"}), 404

        db.session.delete(article)
        db.session.commit()

        articles = FeaturedArticle.query.filter_by(
            type=article_type).order_by(FeaturedArticle.id.desc()).all()
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

