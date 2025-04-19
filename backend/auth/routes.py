# auth/routes.py
from flask import Blueprint, redirect, request, session, url_for
import os, requests
from urllib.parse import urlencode
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES = "user-read-private user-read-email user-top-read"

@auth_bp.route('/login')
def login():
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    })
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(token_url, data=payload, headers=headers)
    tokens = r.json()
    session['access_token'] = tokens.get('access_token')
    session['refresh_token'] = tokens.get('refresh_token')
    session['expires_at'] = datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
    # Redirect to frontend dashboard after successful auth
    return redirect("http://localhost:3000/dashboard")

@auth_bp.route('/logout')
def logout():
    session.clear() # Clear all session data
    return redirect("http://localhost:3000")