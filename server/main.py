from flask import Blueprint, render_template

# Define a blueprint for public pages
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index2.html")
