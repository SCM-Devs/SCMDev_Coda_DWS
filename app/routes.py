import csv
import requests
import os
from flask import Blueprint, render_template, jsonify, request, url_for, redirect
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
        script_path = os.path.join(os.path.dirname(__file__), "../extime_scraper/main.py")

        if not os.path.exists(script_path):
            return jsonify({"error": f"Fichier introuvable: {script_path}"}), 500

        process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        returncode = process.returncode

        output = stdout.decode("utf-8", errors="ignore")
        error_output = stderr.decode("utf-8", errors="ignore")

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
    print(items_on_page)
    return jsonify({
        "products": items_on_page,
        "total_pages": total_pages,
        "current_page": page
    })

@bp.route('/submit', methods=['POST'])
def submit():
    csv_file = 'app/output/extime_products.csv'
    temp_file = 'app/output/temp_products.csv'
    
    product_id = request.form.get('id')  
    if not product_id:
        return "ID du produit manquant", 400
    
    updates = {
        "brand": request.form.get("brand"),
        "name": request.form.get("name-product"),
        "categorie": request.form.get("category"),
        "nom_d_origine": request.form.get("nom_d_origine"),
        "net_weight": request.form.get("net_weight"),
        "volume": request.form.get("volume"),
        "dimensions": request.form.get("dimensions"),
    }

    updated = False
    with open(csv_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(temp_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames  
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row["id"] == product_id:  
                for key, value in updates.items():
                    row[key] = value
                updated = True
            
            writer.writerow(row)

    if updated:
        os.replace(temp_file, csv_file)  
    else:
        os.remove(temp_file)  

    return redirect(url_for('main.index'))


