from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import db, Produit, User

product_api = Blueprint('product_api', __name__)

@product_api.route('/api/produits', methods=['GET'])
@jwt_required()
def get_produits():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    if user.role == 'admin':
        produits = Produit.query.all()
    else:
        produits = Produit.query.filter_by(user_id=user.id).all()
    return jsonify([produit.to_dict() for produit in produits])

@product_api.route('/api/produits/<int:produit_id>', methods=['GET'])
@jwt_required()
def get_produit(produit_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    produit = Produit.query.get_or_404(produit_id)
    if user.role != 'admin' and produit.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    return jsonify(produit.to_dict())

@product_api.route('/api/produits', methods=['POST'])
@jwt_required()
def create_produit():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    data = request.json
    nom = data.get('nom')
    prix = data.get('prix')
    description = data.get('description', '')
    if not nom or prix is None:
        return jsonify({'error': 'Nom et prix obligatoires'}), 400
    produit = Produit(nom=nom, prix=prix, description=description, user_id=user.id)
    db.session.add(produit)
    db.session.commit()
    return jsonify(produit.to_dict()), 201

@product_api.route('/api/produits/<int:produit_id>', methods=['PUT'])
@jwt_required()
def update_produit(produit_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    produit = Produit.query.get_or_404(produit_id)
    if user.role != 'admin' and produit.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    data = request.json
    produit.nom = data.get('nom', produit.nom)
    produit.prix = data.get('prix', produit.prix)
    produit.description = data.get('description', produit.description)
    db.session.commit()
    return jsonify(produit.to_dict())

@product_api.route('/api/produits/<int:produit_id>', methods=['DELETE'])
@jwt_required()
def delete_produit(produit_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    produit = Produit.query.get_or_404(produit_id)
    if user.role != 'admin' and produit.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    db.session.delete(produit)
    db.session.commit()
    return '', 204
