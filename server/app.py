# server/app.py
from flask import Flask, jsonify
from server.config import Config
from server.extensions import limiter

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # init extensions
    limiter.init_app(app)

    # health first (keeps the app alive even if later imports fail)
    @app.get("/health")
    def health():
        return jsonify(ok=True)

    # register blueprints *inside* the factory
    from server.main import main_bp
    app.register_blueprint(main_bp)

    from server.auth import auth_bp
    app.register_blueprint(auth_bp)

    from server.routes.chat import chat_bp
    app.register_blueprint(chat_bp)

    # error handlers
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded"}), 429

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    # dev-only: allow insecure OAuth if requested
    import os
    if app.debug or os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "0") == "1":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    return app
