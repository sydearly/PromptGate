from flask import Blueprint, request, jsonify, session
from flask_limiter.util import get_remote_address
from openai import OpenAI
from server.extensions import limiter
from server.config import Config
from flask import request
import time

chat_bp = Blueprint("chat", __name__)

# Initialize the OpenAI client once
client = OpenAI(api_key=Config.OPENAI_API_KEY)


@chat_bp.route("/api/chat", methods=["POST"])
@limiter.limit("3 per minute", key_func=lambda: session.get("user", get_remote_address()))
def chat():
    """Handles a chat request from the dashboard."""

    # Basic authentication guard
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    ref = request.referrer or ""
    allowed = Config.ALLOWED_ORIGIN
    if not ref.startswith(allowed):
        return jsonify({"error": "Forbidden: Invalid referrer"}), 403

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    # Safety: prevent huge input and runaway cost
    if len(prompt) > 1500:
        prompt = prompt[:1500] + "… (truncated)"

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # cheapest reliable chat model
            messages=[
                {"role": "system", "content": "You are PromptGate, a concise and helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # cap the response length
            temperature=0.7,
        )

        message = response.choices[0].message.content.strip()
        elapsed = round((time.time() - start_time) * 1000)

        return jsonify({
            "response": message,
            "model": response.model,
            "latency_ms": elapsed
        })

    except Exception as e:
        # Graceful error for UI
        err_msg = str(e)
        print("OpenAI error:", err_msg)
        return jsonify({"error": f"AI service unavailable: {err_msg}"}), 500
