"""
Data processing utilities for cleaning, transforming, and saving product data.
"""

import os
import csv
from datetime import datetime

def clean_product_data(product_data):
    """Clean product data by removing unwanted marketing text and empty fields"""
    # Make a copy of the data to avoid modifying the original
    cleaned_data = product_data.copy()
    
    # Common marketing texts to filter out
    marketing_texts = [
        "400 points donnent droit à un bon cadeau de 10€ HT",
        "Bienvenue sur Extime, votre escale plaisir",
        "Offre soumise à conditions",
        "*Jeu organisé par la société Aéroports de Paris",
    ]
    
    # Maximum length for text fields
    max_text_length = 500
    
    # Text fields that need cleaning
    text_fields = ['usage_tips', 'perfume_type_detailed']
    
    # Clean text fields
    for field in text_fields:
        if field in cleaned_data and cleaned_data[field]:
            # Skip if the field is None
            if cleaned_data[field] is None:
                continue
                
            # Check if the field contains marketing text
            for marketing_text in marketing_texts:
                if cleaned_data[field] and marketing_text in cleaned_data[field]:
                    cleaned_data[field] = None
                    break
            
            # Truncate overly long text
            if cleaned_data[field] and len(cleaned_data[field]) > max_text_length:
                cleaned_data[field] = cleaned_data[field][:max_text_length] + "..."
    
    # Ensure special_offers is properly formatted
    if 'special_offers' in cleaned_data and isinstance(cleaned_data['special_offers'], list):
        # Filter out marketing texts
        cleaned_data['special_offers'] = [
            offer for offer in cleaned_data['special_offers']
            if not any(marketing_text in offer for marketing_text in marketing_texts)
        ]
    
    return cleaned_data

def standardize_volume(details):
    """Convert volume to ml for consistency"""
    if details['volume'] and 'cl' in details['volume'].lower():
        try:
            volume_value = float(details['volume'].lower().replace('cl', '').strip()) * 10
            details['volume'] = f"{volume_value} ml"
        except ValueError:
            pass
    elif details['volume'] and 'l' in details['volume'].lower() and 'ml' not in details['volume'].lower():
        try:
            volume_value = float(details['volume'].lower().replace('l', '').strip()) * 1000
            details['volume'] = f"{volume_value} ml"
        except ValueError:
            pass
    return details

def postprocess_product_data(products):
    """
    Post-process all collected product data to fix issues and improve quality
    """
    # This function can be expanded in the future for additional cleaning steps
    return products

def load_existing_data(filename):
    """Load existing data from a CSV file into a dictionary."""
    existing_data = {}
    max_id = 0
    
    if os.path.exists(filename):
         with open(filename, 'r', encoding='utf-8') as f:
             reader = csv.DictReader(f)
             for row in reader:
                 # Use a unique entifier for each product, e.g., 'url_origine' for parfums
                 key = row.get('url_origine') or row.get('product_url')
                 if key:
                     existing_data[key] = row
                    
                 # Track the maximum ID
                 if 'id' in row and row['id'] and row['id'].isdigit():
                     max_id = max(max_id, int(row['id']))
    
    return existing_data, max_id

def save_to_csv(data, filename):
    try:
        # Base filename
        base_filename = os.path.splitext(filename)[0]
        general_filename = f"{base_filename}.csv"

        # Champs du CSV
        fieldnames = [
            'id', 'brand', 'name', 'type_size', 'product_url', 'image_url',
            'scraped_date', 'net_weight', 'categorie', 'url_origine', 'volume',
            'materiaux', 'nom_d_origine', 'dimensions', 'status'
        ]

        # Charger les données existantes pour obtenir le max ID
        existing_data, max_id = load_existing_data(general_filename)

        # Supprimer les doublons basés sur 'url_origine' ou 'product_url'
        unique_data = []
        seen_urls = set()

        for item in data:
            key = item.get('product_url') or item.get('url_origine')
            if key and key not in seen_urls:
                seen_urls.add(key)

                # Assigner un ID unique si le produit n'en a pas
                if 'id' not in item or not item['id']:
                    max_id += 1
                    item['id'] = str(max_id)

                unique_data.append(item)

        # Écriture du fichier CSV (VIDE l'ancien et écrit seulement les nouveaux produits)
        with open(general_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_data)
            for item in unique_data:
                print(item)

        print(f"Enregistré {len(unique_data)} produits dans {general_filename}")

        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du CSV : {e}")
        return False


