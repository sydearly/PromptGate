from flask import Flask, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from server.config import Config
from server.auth import auth_bp
from server.main import main_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Register both blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/")
def index():
    return render_template("index2.html")
