from flask import Flask, jsonify
def create_app():
    app = Flask(__name__)
    @app.get("/health")
    def health():
        return jsonify(ok=True)
    return app
