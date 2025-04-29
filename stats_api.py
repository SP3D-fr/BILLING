from flask import Blueprint, jsonify
from models import db, Client, Facture
from sqlalchemy import func, extract
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import json

stats_api = Blueprint('stats_api', __name__)

@stats_api.route('/api/statistiques', methods=['GET'])
@jwt_required()
def statistiques():
    user = get_jwt_identity()
    # Correction : décoder si string JSON
    if isinstance(user, str):
        try:
            user = json.loads(user)
        except Exception:
            user = {}
    user_id = user['id'] if user and 'id' in user else None
    is_admin = user and user.get('role') == 'admin'
    try:
        # Filtrage des factures et clients par user_id (sauf admin)
        facture_query = Facture.query
        client_query = Client.query
        if not is_admin:
            facture_query = facture_query.filter(Facture.user_id == user_id)
            client_query = client_query.filter(Client.user_id == user_id)

        # Chiffre d'affaires total
        total_ca = facture_query.with_entities(func.sum(Facture.montant)).scalar()
        total_ca = float(total_ca) if total_ca not in (None, '') else 0.0

        # Nombre de factures
        nb_factures = facture_query.count()

        # Nombre de factures payées (statut contient 'pay')
        nb_payees = facture_query.filter(Facture.statut.ilike('%pay%')).count()
        nb_impayees = nb_factures - nb_payees

        # Top 3 clients par CA
        top_clients = db.session.query(
            Client.nom, func.sum(Facture.montant).label('ca')
        ).join(Facture, Facture.client_id == Client.id)
        if not is_admin:
            top_clients = top_clients.filter(Client.user_id == user_id, Facture.user_id == user_id)
        top_clients = top_clients.group_by(Client.id).order_by(func.sum(Facture.montant).desc()).limit(3).all() or []
        top_clients_list = [{'nom': nom, 'ca': float(ca) if ca not in (None, '') else 0.0} for nom, ca in top_clients]

        # Evolution mensuelle du CA sur l'année en cours
        year = datetime.now().year
        monthly = facture_query.with_entities(
            extract('month', Facture.date), func.sum(Facture.montant)
        ).filter(extract('year', Facture.date) == year)
        monthly = monthly.group_by(extract('month', Facture.date)).order_by(extract('month', Facture.date)).all() or []
        monthly_stats = [{'mois': int(mois), 'ca': float(ca) if ca not in (None, '') else 0.0} for mois, ca in monthly]

        return jsonify({
            'total_ca': total_ca,
            'nb_factures': nb_factures,
            'nb_payees': nb_payees,
            'nb_impayees': nb_impayees,
            'top_clients': top_clients_list,
            'evolution_mensuelle': monthly_stats
        })
    except Exception as e:
        logging.exception('Erreur dans /api/statistiques:')
        return jsonify({'error': str(e)}), 500
