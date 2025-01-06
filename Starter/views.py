from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2.extras
import os
from flask_mail import Message
from . import mail
import re


views = Blueprint("views", __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}


def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

#Helper function to validate email
def is_valid_email(email):
    """Validates the format of an email address."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

# Subscriber Helper function to send an email to the admin
def subscriber_email_to_admin(email):
    try:
        admin_email = "bernardomuse22@gmail.com"  
        msg = Message(
            subject="New Subscription Received",
            recipients=[admin_email],
            body=f"""
                You have received a new subscription:
                Email: {email}
            """
        )
        mail.send(msg)
        print("Email sent to admin successfully.")
    except Exception as e:
        print(f"Failed to send email to admin: {str(e)}")


#Subscriber Helper function to send an email to the client
def subscriber_email_to_client(email):
    try:
        msg = Message(
            subject="Thank You for Subscribing",
            recipients=[email],
            body=f"""
            Hi {email},
            Thank you for subscribing to us. We have received your subscription and will keep you updated.
            Best Regards,
            Masika and Koross Advocates
            """
        )
        mail.send(msg)
        print("Email sent to client successfully.")
    except Exception as e:
        print(f"Failed to send email to client: {str(e)}")

#Message Helper function to send an email to the admin
def send_email_to_admin(name, phone_number, email, texts):
    try:
        admin_email = "skmasika@gmail"  
        msg = Message(
            subject="New Message Received",
            recipients=[admin_email],
            body=f"""
                You have received a new message:
                Name: {name}
                Phone Number: {phone_number}
                Email: {email}
                Message: {texts}
            """
        )
        mail.send(msg)
        print("Email sent to admin successfully.")
    except Exception as e:
        print(f"Failed to send email to admin: {e}")


# Message  Helper function to send an email to the client
def send_email_to_client(name, email):
    try:
        msg = Message(
            subject="Thank You for Contacting Us",
            recipients=[email],
            body=f"""
                Hi {name},

                Thank you for reaching out to us. We have received your message and will get back to you shortly.

                Best Regards,
                Masika and Koross Advocates
            """
        )
        mail.send(msg)
        print("Email sent to client successfully.")
    except Exception as e:
        print(f"Failed to send email to client: {e}")
        
        

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

#Message Routes
@views.route("/add_message", methods=["POST"])
def add_message():
    if request.method == "POST":
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        texts = request.form["texts"]

        # Debug: Print the input data
        # print(f"Name: {name}, Phone: {phone_number}, Email: {email}, Texts: {texts}")

        # Validate input
        if not name or not phone_number or not email or not texts:
            flash("All fields are required.")
            return redirect(url_for("views.home"))

        try:
            # Insert into the database
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(
                        "INSERT INTO messages (name, phone_number, email, texts) VALUES (%s, %s, %s, %s)",
                        (name, phone_number, email, texts),
                    )
                    conn.commit()

            # Send emails to admin and client
            send_email_to_admin(name, phone_number, email, texts)
            send_email_to_client(name, email)

            flash("Message sent successfully! An email confirmation has been sent.")
            return redirect(url_for("views.home"))

        except Exception as e:
            # Rollback and log the error
            print(f"Database Error: {e}")
            flash("An error occurred while sending your message. Please try again.")
            return redirect(url_for("views.home"))
    return render_template("home.html")



@views.route("/edit/<int:id>", methods=["GET", "POST"])
def get_message(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == "POST":
            name = request.form["name"]
            phone_number = request.form["phone_number"]
            email = request.form["email"]
            texts = request.form["texts"]
            # Validate input
            if not name or not phone_number or not email or not texts:
                flash("All fields required.")
                return redirect(url_for("views.get_message", id=id))

            try:
                cur.execute(
                    """
                UPDATE messages
                SET name = %s, phone_number = %s, email = %s, texts = %s
                WHERE id = %s
                """,
                    (name, phone_number, email, texts, id),
                )
                conn.commit()
                flash("Message updated successfully!")
                return redirect(url_for("auth.admin_dashboard"))
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}")
                return redirect(url_for("views.get_message", id=id))

        # Fetch message details for GET request
        cur.execute("SELECT * FROM messages WHERE id = %s", (id,))
        message = cur.fetchone()

    except Exception as e:
        flash(f"Error fetching message: {str(e)}")
        message = None  # Fallback in case of an error
    finally:
        # Ensure resources are properly closed
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
    return render_template("edit_message.html", message=message)


@views.route("/update_message/<id>", methods=["POST"])
def update_message(id):
    if request.method == "POST":
        conn = None  # Declare connection in the outer scope
        cur = None  # Declare cursor in the outer scope
        try:
            name = request.form.get("name")
            phone_number = request.form.get("phone_number")
            email = request.form.get("email")
            texts = request.form.get("texts")

            if not (name and phone_number and email and texts):
                flash("Missing required fields!")
                return redirect(url_for("views.add_message"))

            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Update the message in the database
            cur.execute(
                """
                UPDATE students
                SET name = %s,
                    phone_number = %s,
                    email = %s,
                    texts = %s
                WHERE id = %s
                """,
                (name, phone_number, email, texts, id),
            )
            conn.commit()
            flash("Message Updated Successfully")
        except Exception as e:
            # Rollback transaction if the connection exists
            if conn:
                conn.rollback()
            flash(f"Error: {str(e)}")
        finally:
            # Ensure resources are always closed
            if cur:
                cur.close()
            if conn:
                conn.close()
        return redirect(url_for("auth.admin_dashboard"))


@views.route("/delete/<id>", methods=["POST", "GET"])
def delete_message(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("DELETE FROM messages WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Message Removed Successfully")
        return redirect(url_for("auth.admin_dashboard"))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("views.add_message"))



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

    






