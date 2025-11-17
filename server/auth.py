# server/auth.py
from flask import Blueprint, redirect, request, session, url_for, render_template
from oauthlib.oauth2 import WebApplicationClient
import requests
from server.config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(Config.GOOGLE_DISCOVERY_URL).json()

@auth_bp.route("/login")
def login():
    cfg = get_google_provider_cfg()
    authorization_endpoint = cfg["authorization_endpoint"]

    # exact external URL; force https behind Railway proxy
    redirect_uri = url_for("auth.callback", _external=True, _scheme="https")

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    cfg = get_google_provider_cfg()
    token_endpoint = cfg["token_endpoint"]

    redirect_uri = url_for("auth.callback", _external=True, _scheme="https")

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=redirect_uri,
        code=code,
    )
    token_response = requests.post(
        token_url, headers=headers, data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        session["user"] = userinfo_response.json()["email"]
        return redirect(url_for("auth.dashboard"))
    return "User email not available or not verified.", 400

@auth_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", user=user)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
