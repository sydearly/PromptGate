from flask import Blueprint, render_template, redirect, url_for

# Define a blueprint for public pages
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/login")
def root_login():
    return redirect(url_for("auth.login"))

