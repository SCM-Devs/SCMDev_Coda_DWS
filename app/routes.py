import csv
import requests

from flask import Blueprint, render_template, jsonify, request
from app.models import Product
import subprocess
import sys
from flask_cors import CORS


bp = Blueprint('main', __name__)
CORS(bp)


@bp.route('/')
def index():
    last_scraped_date = None
    try:
        with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                last_scraped_date = row['scraped_date']  
                break  
    except Exception as e:
        last_scraped_date = "Date inconnue"

    return render_template('index.html', scraped_date=last_scraped_date)



@bp.route('/scrap-run', methods=['GET'])
def scrap_run():
    try:
        # 🔹 Lancer le script Python de scraping
        process = subprocess.Popen([sys.executable, "scrappy.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        returncode = process.returncode

        # 🛠 Gestion de l'encodage de sortie (UTF-8 ou CP1252 pour Windows)
        try:
            output = stdout.decode("utf-8")
        except UnicodeDecodeError:
            output = stdout.decode("cp1252")

        try:
            error_output = stderr.decode("utf-8")
        except UnicodeDecodeError:
            error_output = stderr.decode("cp1252")

        if returncode == 0:
            return jsonify({"message": "Scraping terminé", "output": output}), 200
        else:
            return jsonify({"error": "Erreur lors du scraping", "details": error_output}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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

@bp.route('/<product_name>')
def productSheet(product_name):
    with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['name'] == product_name:
                last_scraped_date = row['scraped_date']  
                product = Product.from_csv_row(row)
                return render_template('productSheet.html', product=product, scraped_date=last_scraped_date)
    return 'Product not found', 404
   

@bp.route('/search')
def search():    
    query = request.args.get('q', '').lower() 
    page = request.args.get('page', 1, type=int)
    per_page = 30
    products = []

    if not query:
        return jsonify({"error": "Aucun terme de recherche fourni"}), 400

    try:
        with open('app/output/extime_products.csv', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                if query in row['name'].lower():
                    product = Product.from_csv_row(row)
                    products.append(product.convert_to_dic())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    total_pages = (len(products) + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    items_on_page = products[start:end]

    return jsonify({
        "products": items_on_page,
        "total_pages": total_pages,
        "current_page": page
    })
    


