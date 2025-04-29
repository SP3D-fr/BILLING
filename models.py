from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telephone = db.Column(db.String(30), nullable=True)
    adresse = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    factures = db.relationship('Facture', backref='client', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'user_id': self.user_id
        }

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prix': self.prix,
            'description': self.description,
            'user_id': self.user_id
        }

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    montant = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default='En attente')
    reduction_type = db.Column(db.String(10), nullable=True)  # 'euro' ou 'percent'
    reduction_value = db.Column(db.Float, nullable=True, default=0)
    lignes = db.relationship('LigneFacture', backref='facture', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'montant': self.montant,
            'statut': self.statut,
            'reduction_type': self.reduction_type,
            'reduction_value': self.reduction_value,
            'lignes': [ligne.to_dict() for ligne in self.lignes]
        }

class LigneFacture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    produit = db.relationship('Produit')

    def to_dict(self):
        return {
            'id': self.id,
            'facture_id': self.facture_id,
            'produit_id': self.produit_id,
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'produit': self.produit.to_dict() if self.produit else None
        }

class CalculImpression3D(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    nom_produit = db.Column(db.String(120), nullable=False)
    temps_impression = db.Column(db.Float, nullable=False)
    poids_filament = db.Column(db.Float, nullable=False)
    marge = db.Column(db.Float, nullable=False)
    prix_final = db.Column(db.Float, nullable=False)
    prix_arrondi = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'nom_produit': self.nom_produit,
            'temps_impression': self.temps_impression,
            'poids_filament': self.poids_filament,
            'marge': self.marge,
            'prix_final': self.prix_final,
            'prix_arrondi': self.prix_arrondi,
            'description': self.description,
            'user_id': self.user_id
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' ou 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(128), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Settings(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {'key': self.key, 'value': self.value, 'user_id': self.user_id}
