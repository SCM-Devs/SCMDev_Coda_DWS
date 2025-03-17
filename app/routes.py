from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

# Route d'accueil
@bp.route('/')
def index():
    return render_template('index.html')  # Rendre le template index.html
