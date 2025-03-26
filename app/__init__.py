from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configuration de la clé secrète pour les sessions
    app.secret_key = 'votre_cle_secrete'  # Changez ceci pour une clé secrète plus sécurisée

    # Enregistrement des blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app