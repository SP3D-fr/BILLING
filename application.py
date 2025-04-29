print('=== DEMARRAGE BACKEND ACTIF ===')

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from client_api import client_api
from product_api import product_api
from invoice_api import invoice_api
from invoice_pdf import invoice_pdf_api
from stats_api import stats_api
from export_api import export_api
from settings_api import settings_api
from calcul_impression_api import calcul_impression_api
from calcul_historique_api import calcul_historique_api
from models import db, User
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from auth import bp as auth_bp, mail as mail_ext
from werkzeug.security import generate_password_hash

app = Flask(__name__)
# CORS restreint à l'origine frontend
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "https://billingfront.onrender.com"
]}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facturation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configs complémentaires pour l'authentification et l'email
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['JWT_SECRET_KEY'] = 'change_this_jwt_secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ppswarn@gmail.com'
app.config['MAIL_PASSWORD'] = 'qtuh vzal dmae oqpx'
app.config['MAIL_DEFAULT_SENDER'] = 'ppswarn@gmail.com'

db.init_app(app)
jwt = JWTManager(app)
mail_ext.init_app(app)

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    print('DEBUG JWT unauthorized: Token manquant ou invalide. Raison:', reason)
    return jsonify({'error': 'Token manquant ou invalide'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    print('DEBUG JWT invalid: Token mal formé ou expiré. Raison:', reason)
    return jsonify({'error': 'Token invalide'}), 401

app.register_blueprint(client_api)
app.register_blueprint(product_api)
app.register_blueprint(invoice_api)
app.register_blueprint(invoice_pdf_api)
app.register_blueprint(stats_api)
app.register_blueprint(export_api)
app.register_blueprint(settings_api)
app.register_blueprint(calcul_impression_api)
app.register_blueprint(calcul_historique_api)
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return "Backend SP3D Billing API opérationnel !"

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/debug/settings')
def debug_settings():
    from models import Settings
    return {'settings': [(s.key, s.value) for s in Settings.query.all()]}

# Handler global pour afficher toute exception et la stacktrace
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print('DEBUG GLOBAL ERROR:', repr(e))
    traceback.print_exc()
    return jsonify({'error': str(e)}), 500

# Création automatique des tables si besoin
def create_tables():
    with app.app_context():
        db.create_all()

# Création automatique de l'utilisateur admin si inexistant
def create_admin():
    with app.app_context():
        create_tables()
        if not User.query.filter_by(email='lepez.antoine@gmail.com').first():
            admin = User(
                email='lepez.antoine@gmail.com',
                password_hash=generate_password_hash('Leysen62$'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin créé : lepez.antoine@gmail.com')
        else:
            print('Admin déjà existant')

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)
