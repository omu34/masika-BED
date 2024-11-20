from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2.extras
import os
from .models import FeaturedArticle, db
from flask_mail import Message
from Starter import mail



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


# Helper function to send an email to the admin
def send_email_to_admin(name, phone_number, email, texts):
    try:
        admin_email = "admin@example.com"  # Replace with admin email
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


# Helper function to send an email to the client
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


@views.route("/edit/<int:id>", methods=["GET", "POST"])
def get_message(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        texts = request.form["texts"]

        try:
            cur.execute(
                """
                UPDATE messages
                SET fullname = %s, phone_number = %s,email = %s, texts = %s
                WHERE id = %s
            """,
                (name, phone_number, email, texts, id),
            )
            conn.commit()
            flash("message updated successfully!")
            return redirect(url_for("views.message"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
            conn.close()

    cur.execute("SELECT * FROM messages WHERE id = %s", (id,))
    message = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit_message.html", message=message)


@views.route("/update_message/<id>", methods=["POST"])
def update_message(id):
    if request.method == "POST":
        try:
            name = request.form.get("name")
            phone_number = request.form.get("phone_number")
            email = request.form.get("email")
            texts = request.form.get("texts")

            if not (name and phone_number and email and texts):
                flash("Missing required fields!")
                return redirect(url_for("views.message"))

            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            cur.close()
            conn.close()
            flash("Message Updated Successfully")
            return redirect(url_for("views.message"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")


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
        return redirect(url_for("views.message"))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("views.message"))


@views.route("/add_subscriber", methods=["GET", "POST"])
def add_subscriber():
    if request.method == "POST":
        email = request.form["email"]

        # Save to the database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            cur.execute(
                "INSERT INTO subscribers (email) VALUES (%s)",
                (email,)  # Ensure this is passed as a tuple
            )
            conn.commit()

            # Send email to the subscriber
            subscriber_message = Message(
                subject="Subscription Confirmation",
                recipients=[email],  # Client's email
                body=f"Thank you for subscribing to our service, {email}!\n\nWe're excited to have you with us!"
            )
            mail.send(subscriber_message)

            # Send email notification to the admin
            admin_email = 'bernardomuse22@gmail.com'  # Replace with the admin's email
            admin_message = Message(
                subject="New Subscriber",
                recipients=[admin_email],  # Admin's email
                body=f"A new subscriber has joined:\n\nEmail: {email}"
            )
            mail.send(admin_message)

            flash("Subscriber added successfully and emails sent!")
            return redirect(url_for("views.home"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
            conn.close()

    return render_template("home.html")


@views.route("/edit/<int:id>", methods=["GET", "POST"])
def get_subscriber(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        email = request.form["email"]

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
            flash("subscriber updated successfully!")
            return redirect(url_for("views.subscriber"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
            conn.close()

    cur.execute("SELECT * FROM subscribers WHERE id = %s", (id,))
    subscriber = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit_subscriber.html", subscriber=subscriber)


@views.route("/update_subscriber/<id>", methods=["POST"])
def update_subscriber(id):
    if request.method == "POST":
        try:
            email = request.form.get("email")

            if not (email):
                flash("Missing required fields!")
                return redirect(url_for("views.subscriber"))

            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(
                """
                UPDATE students
                SET 
                    email = %s
                WHERE id = %s
            """,
                (email, id),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("subscriber Updated Successfully")
            return redirect(url_for("views.subscriber"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")


@views.route("/delete/<id>", methods=["POST", "GET"])
def delete_subscriber(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("DELETE FROM subscribers WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("subscriber Removed Successfully")
        return redirect(url_for("views.subscriber"))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("views.subscriber"))






@views.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get("is_admin"):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for("featured_articles_section"))

    if request.method == "POST":
        article_id = request.form.get("article_id")
        article = FeaturedArticle.query.get(article_id)
        if article:
            article.is_featured = not article.is_featured
            db.session.commit()
        return redirect(url_for("admin_panel"))

    articles = FeaturedArticle.query.all()
    return render_template("admin_panel.html", articles=articles)

# Featured articles section
@views.route("/featured_articles")
def featured_articles_section():
    articles = FeaturedArticle.query.filter_by(is_featured=True).all()
    return render_template("featured_articles.html", articles=articles)
