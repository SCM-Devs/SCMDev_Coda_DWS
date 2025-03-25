from flask import Flask


def create_app():
    app = Flask(__name__)
<<<<<<< HEAD
    # Configuration de l'application (optionnel pour cette démo)
    app.config['SECRET_KEY'] = 'votre_clé_secrète'
    
    # Importer les routes
=======
    
>>>>>>> 66dcc0d1797c1c6ceb6a944bfb78b1bdb08a7091
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app
