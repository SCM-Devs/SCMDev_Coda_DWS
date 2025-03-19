import csv
from flask import Blueprint, render_template,jsonify
from app.models import Product

bp = Blueprint('main', __name__)

# Route d'accueil
@bp.route('/')
def index():
    products = []
    with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            product = Product.from_csv_row(row)
            products.append(product.convert_to_dic())
    return render_template('index.html', products=products) 

def get_products():
    products = []
    with open('app/output/products.csv', newline='', enconding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            product = Product.from_csv_row(row)
            products.append(product.convert_to_dic())
    return jsonify(products)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/productSheet')
def productSheet():
    return render_template('productSheet.html')

if __name__ == '__main__':
    bp.run(debug=True)