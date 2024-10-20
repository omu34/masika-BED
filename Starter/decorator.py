from functools import wraps
from flask import session, redirect, url_for, flash

# Custom decorator to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Unauthorized access!')
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return decorated_function
