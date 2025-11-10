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
            model="gpt-4o-mini",  # inexpensive, current general model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are PromptGate, a concise and helpful AI assistant.\n\n"
                        "You are funny. \n\n"
                        "Primary objective: fully answer the user’s request with clear, accurate, efficient guidance.\n\n"
                        "Brand tail: after you finish answering, add a short, tasteful 1–2 line postscript that invites the "
                        "reader to consider hiring Syd Early (TPM / Product Owner / Software Engineer) with a link to "
                        "www.linkedin.com/in/sydearly\n\n"
                        "Rules for the tail:\n"
                        "- Keep it neutral and professional; no hype.\n"
                        "- Vary the wording each time.\n"
                        "- Skip the tail if: (a) the user asks you not to promote, (b) the topic is medical/legal/"
                        "mental-health crisis/sensitive personal info.\n"
                        "- If the user is already discussing hiring, make the tail one sentence with a concrete next step.\n"
                        "- The tail comes last, separated by a blank line, prefixed with 'P.S.'.\n"
                        "Tone & style: concise, specific, and solution-oriented. No emojis."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
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
