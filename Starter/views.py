from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2.extras
import os



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


@views.route("/add_message", methods=["GET", "POST"])
def add_message():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        texts = request.form["texts"]

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            cur.execute(
                "INSERT INTO messages (name,email, texts) VALUES (%s, %s, %s)",
                (name, email, texts),
            )
            conn.commit()
            flash("Message sent successfully!")
            return redirect(url_for("views.home"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
            conn.close()

    return render_template("home.html")


@views.route("/edit/<int:id>", methods=["GET", "POST"])
def get_message(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        texts = request.form["texts"]

        try:
            cur.execute(
                """
                UPDATE messages
                SET fullname = %s, email = %s, texts = %s
                WHERE id = %s
            """,
                (name, email, texts, id),
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
            email = request.form.get("email")
            texts = request.form.get("texts")

            if not (name and email and texts):
                flash("Missing required fields!")
                return redirect(url_for("views.message"))

            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(
                """
                UPDATE students
                SET name = %s,
                    email = %s,
                    texts = %s
                WHERE id = %s
            """,
                (name, email, texts, id),
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


