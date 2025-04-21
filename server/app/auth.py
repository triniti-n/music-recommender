from flask import Blueprint, redirect, request, session, url_for
import os, requests
from urllib.parse import urlencode

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES = "user-read-private user-read-email user-top-read"

@auth_bp.route('/login')
def login():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?client_id={client_id}"
        "&response_type=code"
        "&redirect_uri={redirect_uri}"
        "&scope={scopes}"
    ).format(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scopes="user-read-private user-read-email user-top-read"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
        'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
        'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET')
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to obtain token"}, 400

    data = response.json()
    session['access_token'] = data['access_token']
    session['refresh_token'] = data.get('refresh_token')
    return redirect("http://localhost:3000/dashboard")

@auth_bp.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    return redirect("http://localhost:3000/home")
