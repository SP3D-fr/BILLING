from flask import Blueprint, request, jsonify
from models import db, CalculImpression3D

calcul_historique_api = Blueprint('calcul_historique_api', __name__)

@calcul_historique_api.route('/api/calcul-historique', methods=['GET'])
def get_historique():
    historiques = CalculImpression3D.query.order_by(CalculImpression3D.date.desc()).all()
    return jsonify([h.to_dict() for h in historiques])

@calcul_historique_api.route('/api/calcul-historique', methods=['POST'])
def add_historique():
    data = request.json
    hist = CalculImpression3D(
        nom_produit=data.get('nom_produit'),
        temps_impression=data.get('temps_impression'),
        poids_filament=data.get('poids_filament'),
        marge=data.get('marge'),
        prix_final=data.get('prix_final'),
        prix_arrondi=data.get('prix_arrondi'),
        description=data.get('description')
    )
    db.session.add(hist)
    db.session.commit()
    return jsonify(hist.to_dict()), 201

@calcul_historique_api.route('/api/calcul-historique/<int:calc_id>', methods=['DELETE'])
def delete_historique(calc_id):
    hist = CalculImpression3D.query.get(calc_id)
    if not hist:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(hist)
    db.session.commit()
    return jsonify({'status': 'deleted'})
