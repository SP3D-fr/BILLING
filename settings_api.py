from flask import Blueprint, request, jsonify
from models import db, Settings
from flask_jwt_extended import jwt_required, get_jwt_identity

settings_api = Blueprint('settings_api', __name__)

@settings_api.route('/api/settings', methods=['GET'])
@jwt_required()
def get_settings():
    user = get_jwt_identity()
    if isinstance(user, dict):
        user_id = user.get('id')
        is_admin = user.get('role') == 'admin'
    else:
        user_id = user
        is_admin = False
    # Les settings sont isolés par user sauf pour l'admin
    if is_admin:
        settings = Settings.query.all()
    else:
        settings = Settings.query.filter_by(user_id=user_id).all()
    return jsonify([s.to_dict() for s in settings])

@settings_api.route('/api/settings/<key>', methods=['GET'])
@jwt_required()
def get_setting(key):
    user = get_jwt_identity()
    if isinstance(user, dict):
        user_id = user.get('id')
        is_admin = user.get('role') == 'admin'
    else:
        user_id = user
        is_admin = False
    if is_admin:
        s = Settings.query.get(key)
    else:
        s = Settings.query.filter_by(key=key, user_id=user_id).first()
    if s:
        return jsonify(s.to_dict())
    else:
        return jsonify({'error': 'Not found'}), 404

@settings_api.route('/api/settings/<key>', methods=['PUT'])
@jwt_required()
def update_setting(key):
    user = get_jwt_identity()
    if isinstance(user, dict):
        user_id = user.get('id')
        is_admin = user.get('role') == 'admin'
    else:
        user_id = user
        is_admin = False
    data = request.json
    value = data.get('value')
    if value is None:
        return jsonify({'error': 'Missing value'}), 400
    if is_admin:
        s = Settings.query.get(key)
    else:
        s = Settings.query.filter_by(key=key, user_id=user_id).first()
    if not s:
        s = Settings(key=key, value=value, user_id=user_id)
        db.session.add(s)
    else:
        s.value = value
    db.session.commit()
    return jsonify(s.to_dict())

# Ajout des paramètres d'impression 3D par défaut si absents
@settings_api.route('/api/settings/init-impression3d', methods=['POST'])
@jwt_required()
def init_impression3d_settings():
    user = get_jwt_identity()
    if isinstance(user, dict):
        user_id = user.get('id')
        is_admin = user.get('role') == 'admin'
    else:
        user_id = user
        is_admin = False
    defaults = [
        ('tarif_horaire_machine', '5.0'),
        ('prix_kg_filament', '20.0'),
        ('marge_defaut', '30.0')
    ]
    for key, value in defaults:
        if is_admin:
            s = Settings.query.get(key)
        else:
            s = Settings.query.filter_by(key=key, user_id=user_id).first()
        if not s:
            db.session.add(Settings(key=key, value=value, user_id=user_id))
    db.session.commit()
    return jsonify({'status': 'ok'})
