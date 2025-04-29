from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
from models import db, User

bp = Blueprint('auth', __name__)
mail = Mail()

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        import json
        current = json.loads(get_jwt_identity())
        print('DEBUG admin_required current:', current)
        from models import User
        user = User.query.filter_by(email=current.get('email') if isinstance(current, dict) else None).first()
        if not user or user.role != 'admin':
            print('DEBUG: accès refusé admin')
            return jsonify({'error': 'Accès réservé aux administrateurs'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@bp.route('/api/login', methods=['POST'])
def login():
    print('DEBUG: /api/login appelé')
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        print('DEBUG: Données manquantes ou invalides')
        return jsonify({'message': 'Email et mot de passe requis'}), 400
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        print('DEBUG: Email ou mot de passe incorrect')
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401
    import json
    access_token = create_access_token(identity=json.dumps({'id': user.id, 'role': user.role, 'email': user.email}))
    print('DEBUG: Authentification réussie pour', email)
    return jsonify({
        'token': access_token,
        'email': user.email,
        'role': user.role
    }), 200

@bp.route('/api/password-reset-request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    email = data.get('email', '').strip().lower()  # normalisation
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': "Aucun compte avec ce mail"}), 404
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    # Génère un lien vers le frontend (React) pour la réinitialisation
    reset_url = f"http://localhost:3000/reset/{token}"
    msg = Message('Réinitialisation de votre mot de passe', recipients=[user.email])
    msg.body = f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}\nCe lien expirera dans 1 heure."
    mail.send(msg)
    return jsonify({'message': 'Un lien de réinitialisation a été envoyé à votre adresse e-mail.'})

@bp.route('/api/password-reset/<token>', methods=['POST'])
def password_reset(token):
    data = request.get_json()
    new_password = data.get('password')
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Lien invalide ou expiré.'}), 400
    # Hashage du nouveau mot de passe avec bcrypt
    from werkzeug.security import generate_password_hash
    user.password_hash = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    return jsonify({'message': 'Mot de passe réinitialisé'})

@bp.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    print('DEBUG: entrée dans list_users')
    from models import User
    users = User.query.all()
    print('DEBUG: users trouvés:', users)
    return jsonify([
        {
            'id': u.id,
            'email': u.email,
            'role': u.role
        } for u in users
    ])

@bp.route('/api/users/<int:user_id>', methods=['PATCH'])
@admin_required
def update_user(user_id):
    from models import User
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': "Utilisateur introuvable"}), 404
    if 'role' in data:
        user.role = data['role']
    db.session.commit()
    return jsonify({'message': 'Utilisateur mis à jour'})

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    from models import User
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': "Utilisateur introuvable"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur supprimé'})

@bp.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    from models import User
    data = request.get_json()
    print('DEBUG /api/users POST data:', data)
    email = data.get('email', '').strip().lower()
    role = data.get('role', 'user')
    password = data.get('password')
    if not email or not password:
        print('DEBUG: email or password manquant')
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    if User.query.filter_by(email=email).first():
        print('DEBUG: email déjà utilisé')
        return jsonify({'error': 'Email déjà utilisé'}), 400
    from werkzeug.security import generate_password_hash
    user = User(email=email, role=role, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    try:
        from flask_mail import Message as FlaskMailMessage
        subject = str("Bienvenue sur l'application !")
        msg = FlaskMailMessage(subject=subject, recipients=[user.email])
        msg.body = f"Bonjour {user.email},\n\nVotre compte a été créé avec succès.\n\nBienvenue !"
        mail.send(msg)
    except Exception as e:
        print('Erreur lors de l\'envoi du mail de bienvenue:', e)
    return jsonify({'message': 'Utilisateur créé'})
