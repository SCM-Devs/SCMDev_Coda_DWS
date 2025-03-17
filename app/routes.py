from flask import Blueprint, render_template

# Créer un blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')
