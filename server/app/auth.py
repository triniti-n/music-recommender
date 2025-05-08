from flask import Blueprint, redirect, request, session, url_for, jsonify, make_response
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
        print(f"Failed to obtain token: {response.status_code} - {response.text}")
        return {"error": "Failed to obtain token"}, 400

    data = response.json()

    # Make session permanent first
    session.permanent = True

    # Store tokens in session
    session['access_token'] = data['access_token']
    session['refresh_token'] = data.get('refresh_token')

    # Store token expiration time as naive datetime
    expires_in = data.get('expires_in', 3600)
    session['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()

    # Debug log
    print(f"Tokens stored in session. Session keys: {list(session.keys())}")
    print(f"Session contains access_token: {bool(session.get('access_token'))}")
    print(f"Access token value: {session.get('access_token')[:10]}...")

    # Force session save
    session.modified = True

    # Create a response with redirect
    response = make_response(redirect("http://localhost:3000/search"))

    # Set a session cookie with the access token (no max_age means it's a session cookie)
    response.set_cookie(
        'spotify_access_token',
        data['access_token'],
        # No max_age parameter means it's a session cookie that expires when browser closes
        httponly=True,
        samesite='Lax'
    )

    return response

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear all session data
    session.clear()

    # Create a response with redirect for GET requests or JSON response for POST
    if request.method == 'GET':
        response = make_response(redirect("http://localhost:3000/"))
    else:
        response = make_response(jsonify({"success": True, "message": "Logged out successfully"}))

    # Set security headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # Clear all cookies that might contain auth information
    response.delete_cookie('session')
    response.delete_cookie('spotify_access_token')
    response.delete_cookie('refresh_token')

    # For cross-domain cookies, specify domain
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    domain = frontend_url.split('//')[1].split(':')[0]
    if domain != 'localhost':
        response.delete_cookie('session', domain=domain)
        response.delete_cookie('spotify_access_token', domain=domain)
        response.delete_cookie('refresh_token', domain=domain)

    return response

@auth_bp.route('/auth-status')
def auth_status():
    """Debug endpoint to check authentication status"""
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    expires_at = session.get('expires_at')

    # Print session details for debugging
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No session ID'}")
    print(f"Session contains access_token: {bool(access_token)}")
    print(f"Session contains refresh_token: {bool(refresh_token)}")
    print(f"Session keys: {list(session.keys())}")

    # Handle datetime comparison safely
    token_expired = False
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                pass

        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)

        token_expired = datetime.now() > expires_at

    status = {
        'authenticated': bool(access_token),
        'has_refresh_token': bool(refresh_token),
        'token_expires_at': str(expires_at) if expires_at else None,
        'token_expired': token_expired
    }

    return jsonify(status)

@auth_bp.route('/verify-token')
def verify_token():
    """Endpoint to verify if the access token exists in the session"""
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'authenticated': False, 'message': 'No access token found in session'}), 401

    # Check if token is expired
    expires_at = session.get('expires_at')
    token_expired = False

    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                pass

        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)

        token_expired = datetime.now() > expires_at

    if token_expired:
        # Try to refresh the token
        refresh_token = session.get('refresh_token')
        if refresh_token:
            try:
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
                    "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
                }

                response = requests.post("https://accounts.spotify.com/api/token", data=payload)
                if response.status_code == 200:
                    tokens = response.json()
                    session['access_token'] = tokens.get('access_token')
                    session['expires_at'] = datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))

                    # If a new refresh token was provided, update it
                    if 'refresh_token' in tokens:
                        session['refresh_token'] = tokens['refresh_token']

                    return jsonify({'authenticated': True, 'message': 'Token refreshed successfully'})
                else:
                    return jsonify({'authenticated': False, 'message': 'Failed to refresh token'}), 401
            except Exception as e:
                return jsonify({'authenticated': False, 'message': f'Error refreshing token: {str(e)}'}), 500
        else:
            return jsonify({'authenticated': False, 'message': 'Token expired and no refresh token available'}), 401

    return jsonify({'authenticated': True, 'message': 'Valid access token found in session'})
