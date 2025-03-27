"""
Functions for scraping product data from product listings and details pages.
"""
import requests
from PIL import Image
from io import BytesIO
import os

import re
import time
import random
import concurrent.futures
from datetime import datetime
from functools import lru_cache
import sys
import os
import requests
from pathlib import Path
from urllib.parse import urlparse

# Add the parent directory to sys.path if this module is run directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import from the package
from extime_scraper.http_utils import get_session, request_with_retry
from extime_scraper.parser_utils import parse_html, extract_volume_from_text, extract_from_structured_elements, BEST_PARSER
from extime_scraper.categories import is_cave_category
from extime_scraper.data_processing import standardize_volume

def extract_product_info(product, is_cave):
    """Extract product info from a product element - function extracted for better performance"""
    # Extract product URL
    product_url = product.get('href')
    if not product_url:
        return None
        
    if product_url and not product_url.startswith('http'):
        product_url = "https://www.extime.com" + product_url
    
    # Extract brand
    brand_element = product.select_one('h3.relative span[title]')
    brand = brand_element.get_text().strip() if brand_element else None
    
    # Extract product name
    name_element = product.select_one('h4.relative span.line-clamp-3')
    product_name = name_element.get_text().strip() if name_element else None
    
    # Skip to next product if we couldn't extract essential info
    if not brand and not product_name:
        return None
    
    # Extract size/type
    size_element = product.select_one('h4.relative span.line-clamp-1')
    type_size = size_element.get_text().strip() if size_element else None
    
    # Extract image URL more efficiently
    img_element = product.find('img')
    image_url = None
    if img_element:
        image_url = img_element.get('src') or img_element.get('data-src')
        if image_url and not image_url.startswith('http'):
            image_url = "https://www.extime.com" + image_url

    # Convert image to webp
    # Convert image to webp
    print("Image URL:", image_url)
    response = requests.get(image_url, timeout=10)
    image = Image.open(BytesIO(response.content))
    print(image.format)
    
    project_root = Path(__file__).parent.parent
    dossier = project_root / "app" / "static" / "images"

    if not os.path.exists(dossier):
        os.makedirs(dossier)

    image_name = product_name.replace(" ", "_")

    parsed_url = urlparse(image_url)
    print(parsed_url)

    # Récupérer seulement le "nom du fichier" dans l'URL
    image_url_part = parsed_url.query.split("_")[1]
    print(image_url_part)
    image_id_part = parsed_url.query.split("_")[-1]
    image_final_part = image_url_part + "_" + image_id_part.split(".")[0]

    if image:
        image.save(os.path.join(dossier, f"{image_name}-{image_final_part}.webp"), "WEBP")
        print(f"{image_name}-{image_final_part}.webp") 
    else:
        print("Erreur : Image non récupérée.")

    # Create product info dictionary based on category
    if is_cave:
        product_info = {
            'brand': brand,
            'name': product_name,
            'type_size': type_size,
            'product_url': product_url,
            'image_url': f"{image_name}-{image_final_part}.webp",
            'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'net_weight': None
        }
    else:
        # Parse type and size for parfum
        perfume_type = None
        if type_size:
            type_match = re.search(r'(Eau de Parfum|Eau de Toilette|Extrait)', type_size)
            perfume_type = type_match.group(1) if type_match else None

        product_info = {
            'brand': brand,
            'name': product_name,
            'categorie': perfume_type,
            'volume': None,
            'url_origine': product_url,
            'image_url': f"{image_name}-{image_final_part}.webp",
            'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'net_weight': None
        }
    # Try to extract volume from type_size only for parfums
    if not is_cave and type_size and not product_info['volume']:
        extracted_volume = extract_volume_from_text(type_size)
        if extracted_volume:
            product_info['volume'] = extracted_volume
    
    return product_info

# Use caching for product details to avoid re-scraping identical URLs
@lru_cache(maxsize=256)
def get_cached_product_details(product_url):
    """Cached version of detailed product information"""
    return scrape_product_details(product_url)

def scrape_product_details(product_url, session=None, retry_count=0, max_retries=3):
    """Scrape detailed information from a product page with retry logic for 403 errors"""
    if not product_url:
        return {}
    
    # Determine if this is a cave product based on URL
    is_cave = is_cave_category(product_url)
    
    # Use provided session or create a new one if none provided
    if session is None:
        session = get_session()
    
    response = request_with_retry(product_url, session, retry_count, max_retries)
    if not response:
        return {}
    
    # Parse the HTML content
    soup = parse_html(response.text)
    
    # Initialize details dictionary with only the requested fields
    details = {
        'net_weight': None,
    }
    
    # Only extract volume for non-cave products
    if not is_cave:
        details['volume'] = None
    
    # Get the full page text once for use in multiple places
    page_text = soup.get_text()
    
    # Only extract volume for non-cave products
    if not is_cave:
        # Extract volume from title or product name if available
        product_title = soup.find('h1')
        if product_title:
            details['volume'] = extract_volume_from_text(product_title.get_text())
        
        # Si volume non trouvé dans le titre, utiliser une approche plus ciblée
        if not details['volume']:
            # Rechercher dans les éléments spécifiques d'abord, puis dans le texte complet si nécessaire
            for selector in ['div.product-details', 'div.product-description', 'section.product-info']:
                if element := soup.select_one(selector):
                    if volume := extract_volume_from_text(element.get_text()):
                        details['volume'] = volume
                        break
            
            if not details['volume']:
                details['volume'] = extract_volume_from_text(page_text)
    
    # Recherche dans les éléments structurés (DL, tables, etc)
    extract_from_structured_elements(soup, details)
    
    # Recherche du poids net
    if not details['net_weight'] and 'WEIGHT_PATTERN' in globals():
        if weight_match := globals()['WEIGHT_PATTERN'].search(page_text):
            details['net_weight'] = weight_match.group(0).strip()
    
    # Convertir le volume en ml si nécessaire (seulement pour les parfums)
    if not is_cave and 'volume' in details and details['volume']:
        details = standardize_volume(details)
    
    return details
