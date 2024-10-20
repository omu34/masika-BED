import os

from flask import (Blueprint, current_app, redirect, render_template, request,
                   url_for)
from flask_socketio import emit
from werkzeug.utils import secure_filename

realtime = Blueprint('realtime', __name__)

# Helper functions


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_image_upload(file, upload_folder):
    """Handles image upload, saves the file, and returns the file path."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return f'/static/uploads/{filename}'
    return None


def emit_updates(update_type, content):
    """Broadcasts updates via socket.io."""
    emit(update_type, content)

# Admin page route


@realtime.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    # Get current banner data and about page data (this could be pulled from a database in production)
    banners = get_banner_data()
    about_pages = get_about_data()

    if request.method == 'POST':
        # Update banner content
        for i in range(1, 9):
            title = request.form.get(f'banner{i}_title')
            subtitle = request.form.get(f'banner{i}_subtitle')
            button_text = request.form.get(f'banner{i}_button_text')
            button_link = request.form.get(f'banner{i}_button_link')
            image = request.files.get(f'banner{i}_image')

            if image:
                image_url = handle_image_upload(
                    image, current_app.config['UPLOAD_FOLDER'])
                banners[f'banner{i}']['image'] = image_url
            banners[f'banner{i}'].update({
                'title': title,
                'subtitle': subtitle,
                'button_text': button_text,
                'button_link': button_link
            })

            # Emit updates via socket.io for each banner
            emit_updates(f'banner{i}_updated', {
                'title': title,
                'subtitle': subtitle,
                'button_text': button_text,
                'button_link': button_link,
                'image': banners[f'banner{i}'].get('image')
            })

        # Update About Us section
        about_title = request.form.get('about_title')
        about_content = request.form.get('about_content')
        about_button_text = request.form.get('button_text')
        about_button_link = request.form.get('button_link')
        about_image = request.files.get('about_image')

        if about_image:
            about_pages['image_url'] = handle_image_upload(
                about_image, current_app.config['UPLOAD_FOLDER'])

        about_pages.update({
            'title': about_title,
            'content': about_content,
            'button_text': about_button_text,
            'button_link': about_button_link
        })

        # Emit updates via socket.io for About Us
        emit_updates('about_updated', {
            'title': about_title,
            'content': about_content,
            'button_text': about_button_text,
            'button_link': about_button_link,
            'image': about_pages['image_url']
        })

        # Save updated data (in production, save to the database)
        save_banner_data(banners)
        save_about_data(about_pages)

        # Redirect to refresh the page
        return redirect(url_for('realtime.admin_page'))

    # Render the admin page with the current banner and about us content
    return render_template('admin_page.html', banners=banners, about_pages=about_pages)

# Data handlers (for simplicity, using in-memory dictionaries. Replace with DB calls in production)


def get_banner_data():
    """Simulate getting banner data. In production, fetch this from the database."""
    return {
        f'banner{i}': {
            'title': f'Banner {i} Title',
            'subtitle': f'Banner {i} Subtitle',
            'button_text': f'Banner {i} Button',
            'button_link': f'/banner{i}_link',
            'image': f'/static/uploads/banner{i}.jpg'
        } for i in range(1, 9)
    }


def get_about_data():
    """Simulate getting about page data. In production, fetch this from the database."""
    return {
        'title': 'About Us Title',
        'content': 'This is the about us content.',
        'button_text': 'Learn More',
        'button_link': '/about_us_link',
        'image_url': '/static/uploads/about_us.jpg'
    }


def save_banner_data(banners):
    """Simulate saving banner data. Replace this with actual DB save logic."""
    print("Saving banner data:", banners)


def save_about_data(about_pages):
    """Simulate saving about page data. Replace this with actual DB save logic."""
    print("Saving about page data:", about_pages)
