import csv
from flask import Blueprint, render_template, request
from app.models import Product

bp = Blueprint('main', __name__)

# Route d'accueil
@bp.route('/')
def index():
    products = []
    
    # Charger les produits des fichiers CSV
    cave_products = load_products_from_csv('app/output/extime_products_cave.csv')
    parfum_products = load_products_from_csv('app/output/extime_products_parfums.csv')
    
    # Combiner les produits
    products.extend(cave_products)
    products.extend(parfum_products)
    
    # Pagination
    page = request.args.get('page', 1, type=int)  # Récupère le numéro de page depuis l'URL
    per_page = 30  # Nombre de produits par page
    total_products = len(products)  # Nombre total de produits
    start = (page - 1) * per_page  # Index de début
    end = start + per_page  # Index de fin
    paginated_products = products[start:end]  # Produits pour la page actuelle

    # Calculer le nombre total de pages
    total_pages = (total_products + per_page - 1) // per_page  # Arrondi vers le haut

    # Déterminer les pages à afficher
    max_displayed_pages = 5
    start_page = max(1, page - 2)  # Commencer à afficher 2 pages avant la page actuelle
    end_page = min(total_pages, start_page + max_displayed_pages - 1)  # Fin de l'affichage

    # Ajuster le début si nécessaire
    if end_page - start_page < max_displayed_pages - 1:
        start_page = max(1, end_page - (max_displayed_pages - 1))

    return render_template('index.html', products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page)

def load_products_from_csv(filename):
    """Load products from a given CSV file."""
    products = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                product = Product.from_csv_row(row)
                products.append(product.convert_to_dic())
    except FileNotFoundError:
        print(f"Le fichier {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors du chargement des produits depuis {filename}: {e}")
    return products

def get_products():
    products = []
    # Vous pouvez également adapter cette fonction si nécessaire
    return jsonify(products)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/productSheet')
def productSheet():
    return render_template('productSheet.html')

if __name__ == '__main__':
    bp.run(debug=True)