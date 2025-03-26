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
                # Use a unique identifier for each product, e.g., 'url_origine' for parfums
                key = row.get('url_origine') or row.get('product_url')
                if key:
                    existing_data[key] = row
                    
                # Track the maximum ID
                if 'id' in row and row['id'] and row['id'].isdigit():
                    max_id = max(max_id, int(row['id']))
    
    return existing_data, max_id

def save_to_csv(data, filename='extime_products.csv'):    
    try:
        # Load existing data and get the highest existing ID
        existing_data, max_id = load_existing_data(filename)

        # Base filename
        base_filename = os.path.splitext(filename)[0]
        general_filename = f"{base_filename}.csv"
        
        # Make sure dimensions is included in fieldnames
        fieldnames = ['id', 'brand', 'name', 'type_size', 'product_url', 'image_url', 
                      'scraped_date', 'net_weight', 'categorie', 'url_origine', 'volume',
                      'materiaux', 'nom_d_origine', 'dimensions']
        
        # Find any extra fields in the data that aren't in fieldnames
        extra_fields = set()
        for item in data:
            for key in item:
                if key not in fieldnames:
                    extra_fields.add(key)
        
        # Add any extra fields to fieldnames
        if extra_fields:
            print(f"Adding extra fields to CSV: {', '.join(extra_fields)}")
            fieldnames.extend(extra_fields)

        # Prepare rows for writing
        rows = []
        current_id = max_id
        
        for item in data:
            key = item.get('product_url') or item.get('url_origine')
            
            if key in existing_data:
                # Update existing entry but keep its ID
                existing_entry = existing_data[key]
                existing_entry.update(item)
                rows.append(existing_entry)
            else:
                # This is a new product, assign a new ID
                current_id += 1
                item['id'] = str(current_id)
                rows.append(item)
            
        with open(general_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated {len(rows)} products in {general_filename}")
        
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False
