from flask import Blueprint, request, jsonify
from models import Settings
import math
from flask_jwt_extended import jwt_required, get_jwt_identity

calcul_impression_api = Blueprint('calcul_impression_api', __name__)

@calcul_impression_api.route('/api/calcul-impression', methods=['POST'])
@jwt_required()
def calcul_impression():
    user = get_jwt_identity()
    if isinstance(user, dict):
        user_id = user.get('id')
        is_admin = user.get('role') == 'admin'
    else:
        user_id = user
        is_admin = False
    data = request.json
    temps_impression = float(data.get('temps_impression', 0))
    poids_filament = float(data.get('poids_filament', 0))
    marge_specifique = data.get('marge_specifique')
    marge_specifique = float(marge_specifique) if marge_specifique not in (None, "") else None

    # Récupère les paramètres utilisateur
    def get_param(key, default):
        if is_admin:
            s = Settings.query.get(key)
        else:
            s = Settings.query.filter_by(key=key, user_id=user_id).first()
        try:
            return float(s.value)
        except:
            return default
    tarif_horaire_machine = get_param('tarif_horaire_machine', 5.0)
    prix_kg_filament = get_param('prix_kg_filament', 20.0)
    marge_defaut = get_param('marge_defaut', 30.0)

    # DEBUG : Affiche les paramètres utilisés dans la console
    print(f"DEBUG calcul : user_id={user_id}, is_admin={is_admin}, tarif_horaire_machine={tarif_horaire_machine}, prix_kg_filament={prix_kg_filament}, marge_defaut={marge_defaut}")

    # Calculs
    cout_filament = (poids_filament / 1000) * prix_kg_filament
    cout_machine = temps_impression * tarif_horaire_machine
    cout_total = cout_filament + cout_machine
    marge = marge_specifique if marge_specifique is not None else marge_defaut
    prix_final = cout_total * (1 + marge / 100)
    prix_arrondi = math.ceil(prix_final)

    return jsonify({
        'cout_filament': round(cout_filament, 2),
        'cout_machine': round(cout_machine, 2),
        'cout_total': round(cout_total, 2),
        'marge': marge,
        'prix_final': round(prix_final, 2),
        'prix_arrondi': prix_arrondi
    })
