# server/app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128))
    query = db.Column(db.String(256))
    search_type = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)