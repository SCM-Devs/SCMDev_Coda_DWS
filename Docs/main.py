import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List, Tuple
import csv
from datetime import datetime
import os
import time

class ScrapingError(Exception):
    pass

class ProductNotFoundError(ScrapingError):
    pass

class AccessBlockedError(ScrapingError):
    pass

class InvalidEANError(ScrapingError):
    pass

@dataclass
class Product:
    ean: str
    name: str
    brand: str
    volume: str
    type: str
    image_url: str

# Update CATEGORIES with better selectors
CATEGORIES = {
    'parfum': {
        'url': 'https://www.extime.com/fr/paris/shopping/beaute/parfum',
        'selectors': [
            'div.product',
            'h2.product-name',
            '.product-card',
            '[data-testid="product-card"]',
            '[class*="ProductCard"]',
            '[class*="product-card"]',
            '[class*="product_card"]',
            'a[href*="/product/"]'
        ]
    },
    'champagne': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/131-champagne',
        'selectors': [
            'div.product',
            'h2.product-name',
            '.product-card',
            '[data-testid="product-card"]',
            '[class*="ProductCard"]',
            '[class*="product-card"]',
            '[class*="product_card"]',
            'a[href*="/product/"]'
        ]
    },
    'spiritueux': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/623-spiritueux',
        'selectors': [
            'div.product',
            'h2.product-name',
            '.product-card',
            '[data-testid="product-card"]',
            '[class*="ProductCard"]',
            '[class*="product-card"]',
            '[class*="product_card"]',
            'a[href*="/product/"]'
        ]
    },
    'vin': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/312-vin',
        'selectors': [
            'div.product',
            'h2.product-name',
            '.product-card',
            '[data-testid="product-card"]',
            '[class*="ProductCard"]',
            '[class*="product-card"]',
            '[class*="product_card"]',
            'a[href*="/product/"]'
        ]
    }
}

def debug_html_structure(soup: BeautifulSoup, url: str):
    """Enhanced debug function to analyze modern JS framework HTML."""
    print(f"\nDEBUG - Analyzing page: {url}")
    
    # Look for product-related elements
    print("\nSearching for product elements:")
    for attr in ['data-testid', 'data-product', 'data-sku', 'data-item']:
        elements = soup.find_all(attrs={attr: True})
        if elements:
            print(f"\nFound elements with {attr}:")
            for el in elements[:3]:
                print(f"- {el.name}: {attr}='{el[attr]}' class='{el.get('class', '')}'")
    
    # Look for product links
    print("\nSearching for product links:")
    links = soup.find_all('a', href=True)
    product_links = [l for l in links if '/product/' in l['href']]
    for link in product_links[:3]:
        print(f"- Link: {link['href']}")
    
    # Look for JSON data
    scripts = soup.find_all('script', type='application/json') + soup.find_all('script', type='application/ld+json')
    if scripts:
        print("\nFound JSON data in scripts:")
        for script in scripts:
            print(f"- Script type: {script.get('type', 'unknown')}")

def get_all_product_eans() -> List[Tuple[str, str]]:
    """Updated product scraping with complete pagination support."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    products_info = []
    
    for section, config in CATEGORIES.items():
        print(f"\nTraitement de la section : {section}")
        page = 1
        no_more_products = False
        previous_products_count = 0
        
        while not no_more_products:
            try:
                url = f"{config['url']}?page={page}"
                print(f"Page {page} - Récupération des produits...")
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all product links on the page
                product_links = []
                for link in soup.find_all('a', href=True):
                    if '/product/' in link['href']:
                        product_links.append(link['href'])
                
                if not product_links:
                    print(f"Plus de produits trouvés à la page {page}")
                    no_more_products = True
                    break
                
                # Check if we're getting the same number of products (indicates last page)
                if len(product_links) == previous_products_count:
                    print("Même nombre de produits que la page précédente, vérification...")
                    if set(product_links) == set([p[0] for p in products_info[-len(product_links):]]):
                        print("Contenu identique détecté, fin de la pagination")
                        no_more_products = True
                        break
                
                previous_products_count = len(product_links)
                
                # Extract product IDs
                for link in product_links:
                    if '-' in link:
                        product_id = link.split('-')[-1]
                        if (product_id, section) not in products_info:  # Avoid duplicates
                            products_info.append((product_id, section))
                            print(f"Nouveau produit trouvé: {product_id}")
                
                print(f"Total produits trouvés: {len(products_info)}")
                page += 1
                time.sleep(2)  # Respectful delay between requests
                
            except Exception as e:
                print(f"Erreur page {page}: {e}")
                break
    
    print(f"\nTotal final: {len(products_info)} produits uniques trouvés")
    return products_info

def scrape_product(product_id: str, category: str) -> Product:
    """Modified to handle Extime's internal product IDs instead of EANs"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    }
    
    try:
        base_url = "https://www.extime.com/fr/paris"
        
        # Get the product page directly using the product ID
        product_url = f"{base_url}/product/{product_id}"
        print(f"Trying to access product with ID: {product_id}")
        
        response = requests.get(product_url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            raise AccessBlockedError("Access blocked by website")
        elif response.status_code == 404:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug information
        print(f"Debug - Page title: {soup.title.text if soup.title else 'No title'}")
        print(f"Debug - URL: {response.url}")

        # Updated selectors for Extime's HTML structure
        name = soup.select_one('h1, .product-name, [data-testid="product-name"]')
        brand = soup.select_one('.brand, [data-testid="product-brand"]')
        volume = soup.select_one('.volume, .capacity, [data-testid="product-volume"]')
        product_type = soup.select_one('.category, [data-testid="product-category"]')
        image = soup.select_one('img[src*="product"], [data-testid="product-image"] img')

        # Extract text/content with fallbacks
        name_text = name.text.strip() if name and hasattr(name, 'text') else 'Unknown'
        brand_text = brand.text.strip() if brand and hasattr(brand, 'text') else 'Unknown'
        volume_text = volume.text.strip() if volume and hasattr(volume, 'text') else 'Unknown'
        type_text = product_type.text.strip() if product_type and hasattr(product_type, 'text') else category
        image_url = image['src'] if image and image.get('src') else ''

        # Use product ID as EAN since we don't have actual EAN codes
        return Product(
            ean=product_id,  # Using product ID instead of EAN
            name=name_text,
            brand=brand_text,
            volume=volume_text,
            type=type_text,
            image_url=image_url
        )
    
    except requests.Timeout:
        raise ScrapingError("Request timed out")
    except requests.RequestException as e:
        raise ScrapingError(f"Network error: {str(e)}")
    except Exception as e:
        raise ScrapingError(f"Parsing error: {str(e)}")

def export_to_csv(products: List[Product], filename: str = None) -> str:
    """Enhanced CSV export with better error handling and formatting."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"products_{timestamp}.csv"
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:  # Use UTF-8 with BOM for Excel
            writer = csv.DictWriter(f, fieldnames=Product.__annotations__.keys())
            writer.writeheader()
            for product in products:
                # Clean up data before writing
                clean_product = asdict(product)
                for key in clean_product:
                    if isinstance(clean_product[key], str):
                        clean_product[key] = clean_product[key].strip().replace('\n', ' ').replace('\r', '')
                writer.writerow(clean_product)
        
        print(f"\nExport CSV réussi: {len(products)} produits")
        print(f"Fichier: {filepath}")
        return filepath
    
    except Exception as e:
        print(f"Erreur lors de l'export CSV: {e}")
        return None

def load_eans_from_file(filename: str) -> List[str]:
    """Load EAN codes from a file."""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def main():
    print("Récupération des produits depuis Extime...")
    products_info = get_all_product_eans()
    
    if not products_info:
        print("Aucun produit trouvé sur le site")
        return
    
    print(f"\nDébut du traitement de {len(products_info)} produits...")
    products = []
    errors = []
    
    for i, (ean, category) in enumerate(products_info, 1):
        print(f"\nProduit {i}/{len(products_info)} ({category})")
        try:
            product = scrape_product(ean, category)
            print(f"✓ {product.name}")
            products.append(product)
        except ScrapingError as e:
            print(f"✗ Erreur: {str(e)}")
            errors.append((ean, str(e)))
    
    if products:
        csv_path = export_to_csv(products)
        if csv_path:
            print(f"\nRésumé:")
            print(f"- Produits exportés: {len(products)}")
            print(f"- Erreurs: {len(errors)}")
            print(f"- Taux de réussite: {len(products)/len(products_info)*100:.1f}%")
    else:
        print("\nAucun produit n'a pu être récupéré")
        if errors:
            print("\nErreurs rencontrées:")
            for ean, error in errors:
                print(f"- {ean}: {error}")

if __name__ == "__main__":
    main()
