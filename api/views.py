from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import re
from .tasks import (
    subscriber_email_to_admin,
    subscriber_email_to_client,
    send_email_to_admin,
    send_email_to_client,
    is_valid_email,
)
from . import get_db_connection, execute_query

views = Blueprint("views", __name__)

# Home Route


@views.route("/")
def index():
    return render_template("index.html")


@views.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@views.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    return render_template('admin_page.html')


@views.route("/start")
def start():
    if "loggedin" in session:
        return render_template("home.html", email=session["email"])
    return redirect(url_for("auth.login"))


@views.route("/admins")
def admins():
    if "loggedin" in session:
        return render_template("admin_dashboard.html", email=session["email"])
    return redirect(url_for("admin.admin_login"))


# Add Message Route
@views.route("/add_message", methods=["POST"])
def add_message():
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    texts = request.form.get('texts')

    # Debugging
    print(
        f"Received -> Name: {name}, Email: {email}, Phone: {phone_number}, Texts: {texts}")

    # Input Validation
    if not all([name, email, texts]):
        flash("Name, email, and message are required!", "danger")
        return redirect(url_for('views.home'))

    if phone_number and not re.match(r"^\+?[0-9\- ]+$", phone_number):
        flash("Invalid phone number format!", "danger")
        return redirect(url_for('views.home'))

    try:
        query = """
            INSERT INTO messages (name, phone_number, email, texts)
            VALUES (%s, %s, %s, %s)
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, phone_number, email, texts))
                conn.commit()

        # Send Emails via tasks.py functions
        send_email_to_admin(name, phone_number, email, texts)
        send_email_to_client(name, email)

        flash("Message added and emails sent successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred. Please try again.", "danger")

    return redirect(url_for("views.home"))


# Edit and Update Message
@views.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_message(id):
    if request.method == "POST":
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        texts = request.form.get("texts")

        if not all([name, phone_number, email, texts]):
            flash("All fields are required!", "danger")
            return redirect(url_for("views.edit_message", id=id))

        query = """
            UPDATE messages
            SET name = %s, phone_number = %s, email = %s, texts = %s
            WHERE id = %s
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (name, phone_number, email, texts, id))
                    conn.commit()
            flash("Message updated successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while updating the message.", "danger")

        return redirect(url_for("auth.admin_dashboard"))

    # Fetch message details for editing
    query = "SELECT * FROM messages WHERE id = %s"
    message = execute_query(query, (id,), fetchone=True)
    if not message:
        flash("Message not found.", "danger")
        return redirect(url_for("auth.admin_dashboard"))

    return render_template("edit_message.html", message=message)


# Delete Message
@views.route("/delete/<int:id>", methods=["POST"])
def delete_message(id):
    try:
        query = "DELETE FROM messages WHERE id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (id,))
                conn.commit()
        flash("Message deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while deleting the message.", "danger")

    return redirect(url_for("auth.admin_dashboard"))


# Subscriber Management Routes
@views.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()

    # Debugging
    print(f"Email received: {email}")

    # Validate Email
    if not email or not is_valid_email(email):
        flash("A valid email is required!", "danger")
        return redirect(url_for("views.home"))

    try:
        # Insert email into the database
        query = "INSERT INTO subscribers (email) VALUES (%s)"
        execute_query(query, (email,))

        # Send Emails via tasks.py functions
        subscriber_email_to_admin(email)
        subscriber_email_to_client(email)

        flash("You subscribed successfully! A confirmation email has been sent.", "success")
    except Exception as e:
        print(f"Error occurred: {e}")
        flash("An error occurred while subscribing. Please try again.", "danger")

    return redirect(url_for("views.home"))


@views.route('/delete_subscriber/<int:id>', methods=['POST'])
def delete_subscriber(id):
    """Handles deleting a subscriber"""
    try:
        query = "DELETE FROM subscribers WHERE id = %s"
        execute_query(query, (id,))
        flash("Subscriber deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while deleting the subscriber.", "danger")

    return redirect(url_for("auth.admin_dashboard"))


@views.route("/edit_subscriber/<int:id>", methods=["GET", "POST"])
def edit_subscriber(id):
    try:
        # Fetch subscriber for editing
        query = "SELECT * FROM subscribers WHERE id = %s"
        subscriber = execute_query(query, (id,), fetchone=True)

        if not subscriber:
            flash("Subscriber not found.", "danger")
            return redirect(url_for("auth.admin_dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()

            if not email or not is_valid_email(email):
                flash("A valid email is required!", "danger")
                return redirect(url_for("views.edit_subscriber", id=id))

            # Update subscriber
            query = "UPDATE subscribers SET email = %s WHERE id = %s"
            execute_query(query, (email, id))
            flash("Subscriber updated successfully!", "success")
            return redirect(url_for("auth.admin_dashboard"))

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred. Please try again.", "danger")

    return render_template("edit_subscriber.html", subscriber=subscriber)
