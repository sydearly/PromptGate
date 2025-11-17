from flask import Flask, render_template, jsonify
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address
from server.config import Config
from server.main import main_bp
from flask import Flask
from server.extensions import limiter
from server.routes.chat import chat_bp
from server.auth import auth_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    limiter.init_app(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    app.register_blueprint(chat_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/")
def index():
    return render_template("index.html")


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(RateLimitExceeded)
def handle_ratelimit_error(e):
    return jsonify({
        "error": "Rate limit exceeded. Please wait a moment before sending more prompts."
    }), 429

@app.get("/health")
def health():
    return jsonify(ok=True)