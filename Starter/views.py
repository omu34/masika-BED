from flask import Blueprint, render_template, request, flash, redirect, url_for
from .tasks import (
    subscriber_email_to_admin,
    subscriber_email_to_client,
    send_email_to_admin,
    send_email_to_client,
)
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2.extras
import re
from flask_mail import Message
from . import mail, get_db_connection, execute_query
from .tasks import subscriber_email_to_admin, subscriber_email_to_client, send_email_to_admin, send_email_to_client

views = Blueprint("views", __name__)

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


# Add Message
@views.route("/add_message", methods=["POST"])
def add_message():
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    texts = request.form.get('texts')

    # Debugging
    print(
        f"Received -> Name: {name}, Email: {email}, Phone: {phone_number}, Texts: {texts}")

    # Validation
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

        # Send Emails
        subscriber_email_to_admin(email)
        subscriber_email_to_client(email)

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










@views.route("/add_subscriber", methods=["POST"])
def add_subscriber():

    email = request.form.get("email", "").strip()

    # Debugging
    print(f"Email received: {email}")

    # Validate email
    if not email:
        flash("Email is required.")
        return redirect(url_for("views.home"))

    try:
        # Insert email into the database
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "INSERT INTO subscribers (email) VALUES (%s)", (email,))
                conn.commit()

        # Send emails
        subscriber_email_to_admin(email)
        subscriber_email_to_client(email)

        flash("You subscribed successfully! A confirmation email has been sent.")
    except Exception as e:
        print(f"Error occurred: {e}")
        flash("An error occurred while subscribing. Please try again.")
    return redirect(url_for("views.home"))


@views.route("/edit/<int:id>", methods=["GET", "POST"])
def get_subscriber(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == "POST":
            email = request.form["email"]

            # Validate input
            if not email:
                flash("Email is required.")
                return redirect(url_for("views.get_subscriber", id=id))

            try:
                cur.execute(
                    """
                    UPDATE subscribers
                    SET email = %s
                    WHERE id = %s
                    """,
                    (email, id),
                )
                conn.commit()
                flash("Subscriber updated successfully!")
                return redirect(url_for("auth.admin_dashboard"))
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}")
                return redirect(url_for("views.get_subscriber", id=id))

        # Fetch subscriber details for GET request
        cur.execute("SELECT * FROM subscribers WHERE id = %s", (id,))
        subscriber = cur.fetchone()

    except Exception as e:
        flash(f"Error fetching subscriber: {str(e)}")
        subscriber = None  # Fallback in case of an error
    finally:
        # Ensure resources are properly closed
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

    return render_template("edit_subscriber.html", subscriber=subscriber)


@views.route("/update_subscriber/<int:id>", methods=["POST"])
def update_subscriber(id):
    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Email is required!")
            return redirect(url_for("views.subscriber"))

        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Update the subscriber
            cur.execute(
                """
                UPDATE subscribers
                SET email = %s
                WHERE id = %s
                """,
                (email, id),
            )
            conn.commit()
            flash("Subscriber updated successfully!")
        except Exception as e:
            if conn:
                conn.rollback()  # Rollback if there is an error
            flash(f"Error: {str(e)}")
        finally:
            # Ensure resources are properly closed
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()

        return redirect(url_for("auth.admin_dashboard"))


@views.route('/delete_subscriber/<int:id>', methods=['POST'])
def delete_subscriber(id):
    """handles delete subscriber"""
    print(f"Attempting to delete subscriber with ID: {id}")

    try:

        conn = get_db_connection()
        cur = conn.cursor()

        # Delete the user from the database
        cur.execute("DELETE FROM subscribers WHERE id = %s", (id,))
        conn.commit()

        cur.close()
        conn.close()

        flash('subscriber deleted successfully!')
        return redirect(url_for('auth.admin_dashboard'))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("views.add_subscriber"))
    return conn


@views.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        user_email = request.form['email']  # Get the email entered by the user
        try:
            # Send an email to the user
            msg_to_user = Message(
                'Subscription Successful',
                recipients=[user_email]  # The email entered by the user
            )
            msg_to_user.body = f"Thank you for subscribing to our newsletter, {user_email}!"
            mail.send(msg_to_user)

            # Send an email to the admin
            msg_to_admin = Message(
                'New Subscription Alert',
                # Admin's email address
                recipients=['bernardomuse22@gmail.com']
            )
            msg_to_admin.body = f"New subscription from: {user_email}"
            mail.send(msg_to_admin)

            flash('You have successfully subscribed to the newsletter!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        # Redirect to the homepage or another page
        return redirect(url_for('views.home'))





