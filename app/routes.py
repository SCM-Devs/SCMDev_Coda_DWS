import csv
from flask import Blueprint, render_template, jsonify, request
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
    ITEMS = len(products)
    page = request.args.get('page', 1, type=int)
    per_page = 30
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (ITEMS + per_page -1) // per_page

    items_on_page = products[start:end]

    return render_template('index.html', items_on_page = items_on_page, total_pages = total_pages, page = page) 

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