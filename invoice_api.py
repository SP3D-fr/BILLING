from flask import Blueprint, request, jsonify
from models import db, Facture, LigneFacture, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from mail_utils import send_mail_with_pdf
from invoice_pdf import facture_pdf as generate_pdf, generate_invoice_pdf_bytes
import os

invoice_api = Blueprint('invoice_api', __name__)

@invoice_api.route('/api/factures', methods=['GET'])
@jwt_required()
def get_factures():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    if user.role == 'admin':
        factures = Facture.query.all()
    else:
        factures = Facture.query.filter_by(user_id=user.id).all()
    return jsonify([facture.to_dict() for facture in factures])

@invoice_api.route('/api/factures/<int:facture_id>', methods=['GET'])
@jwt_required()
def get_facture(facture_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    facture = Facture.query.get_or_404(facture_id)
    if user.role != 'admin' and facture.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    return jsonify(facture.to_dict())

@invoice_api.route('/api/factures', methods=['POST'])
@jwt_required()
def add_facture():
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    data = request.json
    facture = Facture(
        client_id=data.get('client_id'),
        user_id=user.id,
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else datetime.utcnow(),
        montant=0,  # sera calculé
        statut=data.get('statut', 'En attente'),
        reduction_type=data.get('reduction_type'),
        reduction_value=data.get('reduction_value', 0)
    )
    db.session.add(facture)
    db.session.flush()  # pour avoir l'id
    total = 0
    for ligne in data.get('lignes', []):
        lf = LigneFacture(
            facture_id=facture.id,
            produit_id=ligne['produit_id'],
            quantite=ligne.get('quantite', 1),
            prix_unitaire=ligne['prix_unitaire']
        )
        total += lf.prix_unitaire * lf.quantite
        db.session.add(lf)
    # Appliquer la réduction
    reduction = data.get('reduction_value', 0) or 0
    if data.get('reduction_type') == 'percent':
        total = total * (1 - reduction / 100)
    elif data.get('reduction_type') == 'euro':
        total = max(0, total - reduction)
    facture.montant = round(total, 2)
    db.session.commit()
    return jsonify(facture.to_dict()), 201

@invoice_api.route('/api/factures/<int:facture_id>', methods=['PUT'])
@jwt_required()
def update_facture(facture_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    facture = Facture.query.get_or_404(facture_id)
    if user.role != 'admin' and facture.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    data = request.json
    facture.client_id = data.get('client_id', facture.client_id)
    if data.get('date'):
        facture.date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    facture.statut = data.get('statut', facture.statut)
    facture.reduction_type = data.get('reduction_type')
    facture.reduction_value = data.get('reduction_value', 0)
    # Supprimer les anciennes lignes
    LigneFacture.query.filter_by(facture_id=facture.id).delete()
    db.session.flush()
    total = 0
    for ligne in data.get('lignes', []):
        lf = LigneFacture(
            facture_id=facture.id,
            produit_id=ligne['produit_id'],
            quantite=ligne.get('quantite', 1),
            prix_unitaire=ligne['prix_unitaire']
        )
        total += lf.prix_unitaire * lf.quantite
        db.session.add(lf)
    reduction = data.get('reduction_value', 0) or 0
    if data.get('reduction_type') == 'percent':
        total = total * (1 - reduction / 100)
    elif data.get('reduction_type') == 'euro':
        total = max(0, total - reduction)
    facture.montant = round(total, 2)
    db.session.commit()
    return jsonify(facture.to_dict())

@invoice_api.route('/api/factures/<int:facture_id>', methods=['DELETE'])
@jwt_required()
def delete_facture(facture_id):
    current = json.loads(get_jwt_identity())
    user = User.query.filter_by(email=current.get('email')).first()
    facture = Facture.query.get_or_404(facture_id)
    if user.role != 'admin' and facture.user_id != user.id:
        return jsonify({'error': 'Accès interdit'}), 403
    db.session.delete(facture)
    db.session.commit()
    return '', 204

@invoice_api.route('/api/factures/<int:facture_id>/send_email', methods=['POST'])
@jwt_required()
def send_facture_email(facture_id):
    # Récupérer le texte personnalisé
    data = request.json or {}
    custom_message = data.get('message', 'Bonjour, veuillez trouver votre facture en pièce jointe.')

    # Récupérer la facture, client, user
    facture = Facture.query.get_or_404(facture_id)
    client = facture.client
    if not client or not client.email:
        return jsonify({'error': "Ce client n'a pas d'adresse email renseignée."}), 400

    # Générer le PDF en mémoire
    pdf_bytes = generate_invoice_pdf_bytes(facture_id)
    pdf_filename = f'Facture_{facture_id}.pdf'

    # Paramètres SMTP fixes pour ppswarn@gmail.com
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    smtp_user = 'ppswarn@gmail.com'
    smtp_password = 'qtuh vzal dmae oqpx'
    sender_name = 'SP3D Printing'
    sender_email = smtp_user

    try:
        send_mail_with_pdf(
            smtp_server, smtp_port, smtp_user, smtp_password,
            sender_name, sender_email,
            client.email,
            f"Votre facture n°{facture_id}",
            custom_message,
            pdf_bytes,
            pdf_filename
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
