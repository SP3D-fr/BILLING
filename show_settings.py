from app import app
from models import db, Settings

with app.app_context():
    print([(s.key, s.value) for s in Settings.query.all()])
