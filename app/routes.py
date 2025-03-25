import csv
import requests

from flask import Blueprint, render_template, jsonify, request
from app.models import Product

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/products')
def get_products():
    products = []
    try:
        with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
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

@bp.route('/<product_name>')
def productSheet(product_name):
    with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['name'] == product_name:
                product = Product.from_csv_row(row)
                return render_template('productSheet.html', product=product)
    return 'Product not found', 404
   

@bp.route('/search')
def search():
    query = request.args.get('q', '').lower()
    products = []

    with open('app/output/products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if query in row['name'].lower():
                product = Product.from_csv_row(row)
                products.append(product.convert_to_dic())
    return jsonify(products)
