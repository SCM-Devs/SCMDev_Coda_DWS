import csv
from flask import Blueprint, render_template,jsonify
from app.models import Product

bp = Blueprint('main', __name__)

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
    with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            product = Product.from_csv_row(row)
            products.append(product.convert_to_dic())
    return jsonify(products)


@bp.route('/<product_name>')
def productSheet(product_name):
    with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['name'] == product_name:
                product = Product.from_csv_row(row)
                return render_template('productSheet.html', product=product)
    return 'Product not found', 404
   


if __name__ == '__main__':
    bp.run(debug=True)