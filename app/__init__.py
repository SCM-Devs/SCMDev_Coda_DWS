from flask import Flask


def create_app():
    app = Flask(__name__)
    # Configuration de l'application (optionnel pour cette démo)
    app.config['SECRET_KEY'] = 'votre_clé_secrète'
    
    # Importer les routes
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app
