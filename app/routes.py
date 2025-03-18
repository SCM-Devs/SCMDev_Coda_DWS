from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

# Route d'accueil
@bp.route('/')
def index():
    return render_template('index.html', name="Camille&Co")  # Rendre le template index.html

@bp.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    bp.run(debug=True)