import csv
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
from app.models import Product, users  # Assurez-vous que le modèle d'utilisateur est importé
from functools import wraps  # Importation de wraps pour le décorateur

bp = Blueprint('main', __name__)

# Définition du décorateur login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vous devez vous connecter pour accéder à cette page.', 'error')
            return redirect(url_for('main.login'))  # Redirige vers la page de connexion
        return f(*args, **kwargs)
    return decorated_function

# Routes protégées
@bp.route('/')
@login_required
def index():
    return render_template('index.html')  # Affiche la page d'index

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:  # Validation de l'utilisateur
            session['username'] = username  # Stocke le nom d'utilisateur dans la session
            return redirect(url_for('main.index'))  # Redirige vers la page d'accueil après connexion
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'error')
            return redirect(url_for('main.login'))  # Redirige vers la page de connexion en cas d'erreur

    return render_template('login.html')

@login_required
@bp.route('/api/products')
def get_products():
    products = []
    try:
        with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                product = Product.from_csv_row(row)
                products.append(product.convert_to_dic()) 
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    page = request.args.get('page', 1, type=int)
    per_page = 30
    total_pages = (len(products) + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    items_on_page = products[start:end]

    return jsonify({
        "products": items_on_page,
        "total_pages": total_pages,
        "current_page": page
    })

@login_required
@bp.route('/<product_name>')
def productSheet(product_name):
    with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['name'] == product_name:
                product = Product.from_csv_row(row)
                return render_template('productSheet.html', product=product)
    return 'Product not found', 404

@login_required
@bp.route('/search')
def search():
    query = request.args.get('q', '').lower()
    products = []

    with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            # Vérifiez si la requête correspond au nom du produit ou à l'EAN
            if query in row['name'].lower() or query in row['ean'].lower():
                product = Product.from_csv_row(row)
                products.append(product.convert_to_dic())
    return jsonify(products)

@login_required
@bp.route('/logout')
def logout():
    session.pop('username', None)  # Supprime l'utilisateur de la session
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.login'))  # Redirige vers la page de connexion