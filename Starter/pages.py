import os
from flask import Blueprint, render_template
import psycopg2.extras

pages = Blueprint("pages", __name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn




@pages.route("/about-us")
def about():
    return render_template("about-us.html")

@pages.route("/contact-us")
def contact_us():
    return render_template("contact_us.html")
    
@pages.route("/procurement")
def procurement():
    return render_template("procurement.html")
    
@pages.route("/legal")
def legal():
    return render_template("legal.html")


@pages.route("/arbitration")
def arbitration():
    return render_template("arbitration.html")
@pages.route("/conveyance")
def conveyance():
    return render_template("conveyance.html")
@pages.route("/family")
def family():
    return render_template("family.html")
@pages.route("/health")
def health():

    return render_template("health.html")
@pages.route("/environment")
def environment():
    return render_template("environment.html")
@pages.route("/constitutional")
def constitutional():
    return render_template("constitutional.html")
@pages.route("/election")
def election():
    return render_template("election.html")



@pages.route("/commercial")
def commercial():

    return render_template("commercial.html")

@pages.route("/banking")
def banking():
    return render_template("banking.html")
@pages.route("/employment")
def employment():
    return render_template("employment.html")


@pages.route("/interlectial")
def interlectial():

    return render_template("interlectial.html")
@pages.route("/tax")
def tax():
    return render_template("tax.html")
@pages.route("/criminal")
def criminal():
    return render_template("criminal.html")