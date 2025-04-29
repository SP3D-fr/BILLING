from models import db, Client, Produit, Facture, CalculImpression3D
from app import app

with app.app_context():
    # Add user_id columns if not exist (SQLite syntax)
    try:
        db.session.execute('ALTER TABLE client ADD COLUMN user_id INTEGER REFERENCES user(id) DEFAULT 1')
    except Exception as e:
        print('Client user_id déjà présent ou erreur:', e)
    try:
        db.session.execute('ALTER TABLE produit ADD COLUMN user_id INTEGER REFERENCES user(id) DEFAULT 1')
    except Exception as e:
        print('Produit user_id déjà présent ou erreur:', e)
    try:
        db.session.execute('ALTER TABLE facture ADD COLUMN user_id INTEGER REFERENCES user(id) DEFAULT 1')
    except Exception as e:
        print('Facture user_id déjà présent ou erreur:', e)
    try:
        db.session.execute('ALTER TABLE calcul_impression3_d ADD COLUMN user_id INTEGER REFERENCES user(id) DEFAULT 1')
    except Exception as e:
        print('CalculImpression3D user_id déjà présent ou erreur:', e)
    db.session.commit()
    print('Migration terminée.')
