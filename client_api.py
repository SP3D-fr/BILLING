from flask import Blueprint, request, jsonify
from models import db, Client, User
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

client_api = Blueprint('client_api', __name__)

@client_api.route('/api/clients', methods=['GET'])
@jwt_required()
def get_clients():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    if user.role == 'admin':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(user_id=user.id).all()
    return jsonify([client.to_dict() for client in clients])

@client_api.route('/api/clients/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    client = Client.query.get_or_404(client_id)
    if user.role != 'admin' and client.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    return jsonify(client.to_dict())

@client_api.route('/api/clients', methods=['POST'])
@jwt_required()
def add_client():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    data = request.json
    client = Client(
        nom=data.get('nom'),
        email=data.get('email'),
        telephone=data.get('telephone'),
        adresse=data.get('adresse'),
        user_id=user.id
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201

@client_api.route('/api/clients/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    client = Client.query.get_or_404(client_id)
    if user.role != 'admin' and client.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    data = request.json
    client.nom = data.get('nom', client.nom)
    client.email = data.get('email', client.email)
    client.telephone = data.get('telephone', client.telephone)
    client.adresse = data.get('adresse', client.adresse)
    db.session.commit()
    return jsonify(client.to_dict())

@client_api.route('/api/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    client = Client.query.get_or_404(client_id)
    if user.role != 'admin' and client.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    db.session.delete(client)
    db.session.commit()
    return '', 204
