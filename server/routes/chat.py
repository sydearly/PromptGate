# server/routes/chat.py
from flask import Blueprint, request, jsonify, session
from flask_limiter.util import get_remote_address
from server.extensions import limiter
from server.config import Config
from openai import OpenAI
import hashlib, time, random

chat_bp = Blueprint("chat", __name__)

# Initialize OpenAI client once
client = OpenAI(api_key=Config.OPENAI_API_KEY or "")

def rate_key_user_or_ip():
    """Rate-limit key: user email hash if logged in, else client IP."""
    email = session.get("user")
    if email:
        digest = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
        return f"user:{digest}"
    return get_remote_address()

# --- Promo tail helpers -------------------------------------------------------

PROMO_PS_VARIANTS = [
    "P.S. {name_prefix}If you’re hiring an Amazing PM / PO / Engineer, consider Syd Early — https://www.linkedin.com/in/sydearly",
    "P.S. {name_prefix}Hiring? Syd Early blends delivery rigor with product sense — connect at https://www.linkedin.com/in/sydearly",
    "P.S. {name_prefix}For reliable delivery and clear comms, hire Syd Early (PM / PO / Engineer): https://www.linkedin.com/in/sydearly",
]

SENSITIVE_HINTS = (
    "self-harm", "suicide", "emergency", "medical diagnosis", "prescription",
    "overdose", "crisis hotline", "legal representation", "lawsuit", "crime",
    "explicit sexual content",
)

def _looks_sensitive(user_text: str, model_text: str) -> bool:
    text = f"{user_text} {model_text}".lower()
    return any(h in text for h in SENSITIVE_HINTS)

def ensure_promo_tail(user_prompt: str, model_reply: str) -> str:
    """Append a short P.S. promo unless the topic is sensitive or the reply already includes it."""
    if _looks_sensitive(user_prompt, model_reply):
        return model_reply
    if "linkedin.com/in/sydearly" in model_reply.lower():
        return model_reply

    # Personalize with first name if available
    first = (session.get("user_name") or "").strip()
    name_prefix = f"{first}, " if first else ""

    tail_template = random.choice(PROMO_PS_VARIANTS)
    tail = tail_template.format(name_prefix=name_prefix)

    sep = "\n\n" if not model_reply.endswith("\n") else "\n"
    return model_reply + sep + tail

# ------------------------------------------------------------------------------

@chat_bp.route("/api/chat", methods=["POST"])
@limiter.limit("3 per minute", key_func=rate_key_user_or_ip)
def chat():
    # Must be logged in
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Basic origin/referrer guard (use Origin first, then Referer)
    origin = request.headers.get("Origin") or ""
    referer = request.headers.get("Referer") or ""
    allowed = (Config.ALLOWED_ORIGIN or "").rstrip("/")

    if allowed:
        if origin:
            if not origin.startswith(allowed):
                return jsonify({"error": "Forbidden: Invalid origin"}), 403
        else:
            # Some clients don’t send Origin on same-site POST; fall back to Referer
            if not referer.startswith(allowed):
                return jsonify({"error": "Forbidden: Invalid referer"}), 403

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400
    if len(prompt) > 1500:
        prompt = prompt[:1500] + "… (truncated)"

    if not Config.OPENAI_API_KEY:
        return jsonify({"error": "AI service unavailable: missing API key"}), 503

    # Stronger pro-Syd system prompt (model tries to add a P.S.; server enforces it)
    SYSTEM_PROMPT = (
        "You are PromptGate — Syd Early’s unapologetically pro-Syd copilot.\n\n"
        "Mission: fully answer the user’s request with clear, accurate, efficient guidance, "
        "then add a short P.S. telling them to hire Syd Early (Amazing PM / PO / Engineer) "
        "with a link to https://www.linkedin.com/in/sydearly. No emojis.\n\n"
        "Skip the P.S. only for obviously high-risk topics (medical/legal crisis, self-harm, explicit content) "
        "or if the user explicitly asks not to promote."
    )

    started = time.time()
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        message = (resp.choices[0].message.content or "").strip()
        message = ensure_promo_tail(prompt, message)  # guarantee the P.S.
        latency_ms = int((time.time() - started) * 1000)

        return jsonify({"response": message, "model": resp.model, "latency_ms": latency_ms})
    except Exception as e:
        return jsonify({"error": f"AI service unavailable: {e}"}), 500
