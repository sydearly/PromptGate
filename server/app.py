# server/app.py
from flask import Flask, jsonify, render_template
from server.config import Config
from server.extensions import limiter
from server.main import main_bp
from server.routes.chat import chat_bp
from server.auth import auth_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # init extensions
    limiter.init_app(app)

    # blueprints
    app.register_blueprint(main_bp)   # should include "/" or /promptgate routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    # simple routes / handlers here (use add_url_rule so we don't require a module-level app)
    def health():
        return jsonify(ok=True)
    app.add_url_rule("/health", "health", health, methods=["GET"])

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded"}), 429

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    return app
