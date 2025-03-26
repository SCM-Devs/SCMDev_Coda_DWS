import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from datetime import datetime
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import random
import lxml
from functools import lru_cache
import multiprocessing

# Find best parser once at module level
def get_best_parser():
    """Determine the best available parser for BeautifulSoup"""
    try:
        import lxml
        return 'lxml'
    except ImportError:
        print("Note: 'lxml' parser not found. Using slower 'html.parser' instead.")
        print("Tip: Install lxml for faster parsing: pip install lxml")
        return 'html.parser'

# Use module-level constant
BEST_PARSER = get_best_parser()

# Cache user agents to avoid repetitive generation
@lru_cache(maxsize=1)
def get_user_agents():
    """Return a list of user agent strings"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]

def get_random_user_agent():
    """Return a random user agent string"""
    return random.choice(get_user_agents())

# Use a connection pool with session reuse
def get_session():
    """Create optimized requests session with retry capabilities and browser-like headers"""
    session = requests.Session()
    
    # Configure retry strategy - don't retry on 403 errors
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Add comprehensive browser-like headers
    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    })
    
    return session

# Pre-compile regex patterns for better performance
VOLUME_PATTERNS = [
    re.compile(r'(\d+(?:[\.,]\d+)?)\s*[mM][lL]'),
    re.compile(r'(\d+(?:[\.,]\d+)?)\s*[cC][lL]'),
    re.compile(r'(\d+(?:[\.,]\d+)?)\s*[lL]'),
    re.compile(r'(?:flacon|bouteille|bottle)(?:\s+de)?\s+(\d+(?:[\.,]\d+)?)\s*[mMcClL][lL]?'),
    re.compile(r'(?:contenance|volume|size)[^\d]*(\d+(?:[\.,]\d+)?)\s*[mMcClL][lL]?')
]
PRICE_VOLUME_PATTERN = re.compile(r'(\d+(?:[\.,]\d+)?)\s*[mMcClL][lL][^\d]*\d+(?:[\.,]\d+)?\s*(?:€|\$|£)')
WEIGHT_PATTERN = re.compile(r'(?:poids net|net wt\.?|weight)[^\d]*(\d+(?:[,.]\d+)?)\s*(?:g|gr|gram|gramme|kg|kilogram)', re.IGNORECASE)

# Liste de phrases à exclure (définie une seule fois)
EXCLUDE_TERMS = [
    "CONDITIONS DE CONSERVATION",
    "À BOIRE DANS LES",
    "REGLEMENTATION",
    "RÉGLEMENTATION",
    "ANS",
    "NOS CLIENTS NOUS FONT CONFIANCE",
    "VOUS POURRIEZ AUSSI AIMER",
    "VOIR TOUS LES PRODUITS",
    "BOIRE DANS LES"
]

# Mapping des pays pour normalisation (défini une seule fois)
COUNTRY_CORRECTIONS = {
    'royaume': 'Royaume-Unis',
    'uk': 'Royaume-Unis',
    'united kingdom': 'Royaume-Unis',
    'angleterre': 'Royaume-Unis',
    'england': 'Royaume-Unis',
    'gb': 'Royaume-Unis',
    'grande bretagne': 'Royaume-Unis',
    'grande-bretagne': 'Royaume-Unis',
    'ecosse': 'Écosse',
    'irlande du nord': 'Royaume-Unis',
    'usa': 'États-Unis',
    'etats-unis': 'États-Unis',
    'etats unis': 'États-Unis',
    'united states': 'États-Unis',
    'fr': 'France',
    'it': 'Italie',
    'es': 'Espagne'
}

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

def extract_volume_from_text(text):
    """Extract volume information from text content using pre-compiled patterns"""
    if not text:
        return None
    
    # Check each pattern
    for pattern in VOLUME_PATTERNS:
        match = pattern.search(text)
        if match:
            # Get the numeric part
            volume_value = match.group(1).replace(',', '.')
            # Get the unit (ml, cl, l)
            unit = text[match.end() - 2:match.end()].lower()
            
            # Format with the unit
            if unit == 'cl':
                return f"{volume_value} cl"
            elif unit in ('l', 'L'):
                return f"{volume_value} L"
            else:  # Default to ml
                return f"{volume_value} ml"
    
    # Look for price patterns that might contain volume
    match = PRICE_VOLUME_PATTERN.search(text)
    if match:
        volume_value = match.group(1)
        return f"{volume_value} ml"
    
    return None

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
    else:
        # Update user agent for this request to vary behavior
        session.headers.update({'User-Agent': get_random_user_agent()})
    
    # Add a referer to appear more browser-like
    session.headers.update({'Referer': "https://www.extime.com/fr/paris/shopping"})
    
    try:
        # Add a random delay to mimic human behavior
        delay = random.uniform(0.5, 1.5)  # Reduced delay range for better efficiency
        print(f"Waiting {delay:.1f}s before fetching {product_url}")
        time.sleep(delay)
        
        response = session.get(product_url)
        
        # Special handling for 403 errors with exponential backoff
        if response.status_code == 403:
            if retry_count < max_retries:
                wait_time = 2 * (2 ** retry_count) + random.uniform(0, 1)
                print(f"403 Forbidden error. Attempt {retry_count + 1}/{max_retries}. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                
                # Create a fresh session for the retry
                new_session = get_session()
                return scrape_product_details(product_url, new_session, retry_count + 1, max_retries)
            else:
                print(f"Maximum retries reached. Failed to fetch {product_url}")
                return {}

        response.raise_for_status()
        
        # Use the best available parser
        soup = BeautifulSoup(response.text, BEST_PARSER)
        
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
        if not details['net_weight']:
            if weight_match := WEIGHT_PATTERN.search(page_text):
                details['net_weight'] = weight_match.group(0).strip()
        
        # Convertir le volume en ml si nécessaire (seulement pour les parfums)
        if not is_cave and 'volume' in details and details['volume']:
            details = standardize_volume(details)
        
        return details
        
    except Exception as e:
        print(f"Error scraping product details: {e}")
        return {}

def extract_from_structured_elements(soup, extracted_attributes):
    """Extract data from structured elements like DL, tables, etc."""
    # Dictionnaire de labels pour la recherche
    labels = {
        'POIDS NET': 'net_weight', 'POIDS': 'net_weight', 'WEIGHT': 'net_weight',
        'GRAMMES': 'net_weight', 'GRAMME': 'net_weight', 'G': 'net_weight', 
        'KILOGRAMMES': 'net_weight', 'KILOGRAMME': 'net_weight', 'KG': 'net_weight',
        'NET WT': 'net_weight', 'NET WEIGHT': 'net_weight',
    }
    
    # Add volume labels only if we're looking for volume
    if 'volume' in extracted_attributes:
        volume_labels = {
            'VOLUME': 'volume', 'CONTENANCE': 'volume', 'CAPACITÉ': 'volume', 
            'CAPACITE': 'volume', 'ML': 'volume', 'CL': 'volume', 'L': 'volume',
            'CONTENU': 'volume', 'QUANTITÉ': 'volume', 'QUANTITE': 'volume',
        }
        labels.update(volume_labels)
    
    # Recherche dans les listes de définition (dt/dd)
    for dl in soup.find_all('dl'):
        dt_elements = dl.find_all('dt')
        dd_elements = dl.find_all('dd')
        
        for i, dt in enumerate(dt_elements):
            if i < len(dd_elements):
                label_text = dt.get_text().strip().upper()
                for label, key in labels.items():
                    if label in label_text and not extracted_attributes[key]:
                        extracted_attributes[key] = dd_elements[i].get_text().strip()
    
    # Recherche dans les tables
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                header_text = cells[0].get_text().strip().upper()
                for label, key in labels.items():
                    if label in header_text and not extracted_attributes[key]:
                        extracted_attributes[key] = cells[1].get_text().strip()
    
    # Recherche dans les divs avec deux-points
    for div in soup.select('div.product-specs, div.product-details, div.specifications'):
        div_text = div.get_text().strip()
        if ':' in div_text:
            parts = div_text.split(':')
            if len(parts) >= 2:
                label_part = parts[0].strip().upper()
                value_part = parts[1].strip()
                for label, key in labels.items():
                    if label in label_part and not extracted_attributes[key]:
                        extracted_attributes[key] = value_part

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

# Category definitions
CATEGORIES = {
    'parfum': {
        'url': 'https://www.extime.com/fr/paris/shopping/beaute/parfum',
    },
    'champagne': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/champagne',
    },
    'spiritueux': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/spiritueux',
    },
    'vin': {
        'url': 'https://www.extime.com/fr/paris/shopping/cave/vin',
    }
}

def get_category_url(category):
    """Get the URL for a specific category"""
    return CATEGORIES.get(category, {}).get('url')

def is_cave_category(base_url):
    """Determine if the URL is for a cave category"""
    return any(category in base_url for category in ['champagne', 'spiritueux', 'vin'])

def scrape_extime_perfumes(base_url="https://www.extime.com/fr/paris/shopping/beaute/parfum", max_products=None, threads=5):
    """Scrape products from the Extime website, with optimized pagination handling"""
    print(f"Starting scraping from {base_url}...")
    
    is_cave = is_cave_category(base_url)
    session = get_session()
    
    # Visit the homepage first to get cookies
    try:
        session.get('https://www.extime.com/fr/paris')
        time.sleep(1)  # Reduced wait time
    except Exception as e:
        print(f"Error visiting homepage: {e}")
    
    all_products = []
    page = 1
    
    # Create a cache for page responses to avoid re-downloading if we need to parse again
    page_cache = {}
    
    while True:
        current_url = f"{base_url}?p={page}" if page > 1 else base_url
        print(f"\nFetching page {page}... ({current_url})")
        
        # Reduced delay between page requests
        time.sleep(random.uniform(1, 2))  # Reduced from 2-4 to 1-2
        
        try:
            # Check if page is in cache first
            if (current_url in page_cache):
                response_text = page_cache[current_url]
                print(f"Using cached page {page}")
            else:
                response = session.get(current_url)
                response.raise_for_status()
                response_text = response.text
                # Store in cache
                page_cache[current_url] = response_text
                # Limit cache size
                if len(page_cache) > 10:
                    # Remove oldest entry
                    page_cache.pop(next(iter(page_cache)))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(response_text, BEST_PARSER)
        
        # Extract total product count on first page
        if page == 1:
            try:
                pagination_info = soup.find('p', class_=lambda c: c and 'text-xsmall' in c)
                if pagination_info:
                    info_text = pagination_info.get_text()
                    match = re.search(r'sur\s+([0-9\s\u202f]+)', info_text)
                    if match:
                        total_products_str = re.sub(r'\s|\u202f', '', match.group(1))
                        total_products = int(total_products_str)
                        print(f"Found {total_products} total products to scrape")
            except Exception as e:
                print(f"Couldn't extract total product count: {e}")
        
        # Find all product elements more efficiently
        product_elements = soup.find_all('a', class_='relative')
        
        if not product_elements:
            print(f"No product elements found on page {page}.")
            break
        
        print(f"Found {len(product_elements)} product elements on page {page}")
        
        # Process each product on the page more efficiently
        # Utilisez la compréhension de liste avec gestion d'erreur pour plus d'efficacité
        page_products = []
        for product in product_elements:
            try:
                # Extract product info
                product_info = extract_product_info(product, is_cave)
                if product_info:
                    page_products.append(product_info)
            except Exception as e:
                print(f"Error extracting product data: {e}")
        
        # Add products from this page to our full list
        all_products.extend(page_products)
        print(f"Added {len(page_products)} products. Total collected: {len(all_products)}")
        
        # Check if we've reached maximum product limit
        if max_products and len(all_products) >= max_products:
            print(f"Reached maximum product limit of {max_products}.")
            all_products = all_products[:max_products]
            break
            
        # Check for next page with optimized detection
        next_page_found = False
        
        # Look for pagination elements
        pagination = soup.select('a.pagination, a[aria-label="Next page"], button.whitespace-no-wrap')
        for elem in pagination:
            text = elem.get_text().lower()
            if ('next' in text or 'suivant' in text or 'afficher plus' in text or 
                str(page + 1) == text.strip()):
                next_page_found = True
                break
        
        if not next_page_found:
            print(f"No navigation to page {page+1} found. This appears to be the last page.")
            break
            
        page += 1
    
    # Fetch detailed information using thread pool
    print(f"\nFetching detailed information for {len(all_products)} products using {threads} threads...")
    
    # Define a worker function that uses caching
    def fetch_details(product):
        is_cave = 'product_url' in product
        url_field = 'product_url' if is_cave else 'url_origine'
        product_url = product.get(url_field)
        
        if product_url:
            # Use cached version if possible
            product_details = get_cached_product_details(product_url)
            
            # Update product with only the needed fields
            if is_cave:
                product.update({
                    'net_weight': product_details.get('net_weight')
                })
            else:
                product.update({
                    'volume': product_details.get('volume') or product.get('volume'),
                    'net_weight': product_details.get('net_weight')
                })
        
        return product
    
    # Process in batches to prevent overloading
    # Optimiser le traitement par lots pour plus d'efficacité
    # Ajuster la taille des lots en fonction du nombre de produits
    batch_size = min(20, max(5, len(all_products) // threads))
    
    products_with_details = []
    
    # Ajouter une option pour des erreurs silencieuses dans les threads
    for i in range(0, len(all_products), batch_size):
        batch = all_products[i:i+batch_size]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(fetch_details, product) for product in batch]
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    product_with_details = future.result()
                    products_with_details.append(product_with_details)
                except Exception as exc:
                    # Traitement d'erreur plus silencieux pour éviter de bloquer
                    print(f'Error processing product: {type(exc).__name__}')
        
        print(f"Processed {min(i + batch_size, len(all_products))} of {len(all_products)} products")
        if len(batch) < batch_size:  # Petite optimisation pour le dernier lot
            time.sleep(0.5)
        else:
            time.sleep(1)  # Small delay between batches
    
    print(f"\nSuccessfully extracted data for {len(products_with_details)} products.")
    
    # Post-process the data to clean and improve the results
    cleaned_products = postprocess_product_data(products_with_details)
    
    return cleaned_products

def postprocess_product_data(products):
    """
    Post-process all collected product data to fix issues and improve quality
    """
    # Since we're removing origin_country, this function can be simplified
    return products

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
    
    # Create product info dictionary based on category
    if is_cave:
        product_info = {
            'brand': brand,
            'name': product_name,
            'type_size': type_size,
            'product_url': product_url,
            'image_url': image_url,
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
            'image_url': image_url,
            'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'net_weight': None
        }
    
    # Try to extract volume from type_size only for parfums
    if not is_cave and type_size and not product_info['volume']:
        extracted_volume = extract_volume_from_text(type_size)
        if extracted_volume:
            product_info['volume'] = extracted_volume
    
    return product_info

def load_existing_data(filename):
    """Load existing data from a CSV file into a dictionary."""
    existing_data = {}
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Use a unique identifier for each product, e.g., 'url_origine' for parfums
                key = row.get('url_origine') or row.get('product_url')
                if key:
                    existing_data[key] = row
    return existing_data

def save_to_csv(data, filename='extime_perfumes.csv'):    
    try:
        # Load existing data
        existing_data = load_existing_data(filename)

        products = []
        
        products = data   
        
        # Base filename
        base_filename = os.path.splitext(filename)[0]

        general_filename = f"{base_filename}.csv"
        fieldnames = ['brand', 'name', 'type_size', 'product_url', 'image_url', 
              'scraped_date', 'net_weight', 'categorie', 'url_origine', 'volume']

            
            # Prepare rows for writing
        rows = []
        for item in products:
            key = item.get('product_url')
            if key in existing_data:
                    # Update existing entry
                existing_data[key].update(item)
                rows.append(existing_data[key])
            else:
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

def main():
    """Main function with optimized execution flow"""
    

    # Chemin vers le répertoire "output" dans le dossier "app"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "output")
    os.makedirs(output_dir, exist_ok=True)

    
    # Use single timestamp for all files
    all_collected_products = []
    
    # Utiliser CPU_COUNT pour un threading optimal
    cpu_count = multiprocessing.cpu_count()
    optimal_threads = max(3, min(cpu_count - 1, 8))  # Au moins 3, au plus 8 threads
    
    # Scrape each category
    for category, details in CATEGORIES.items():
        print(f"\nScraping category: {category}")
        base_url = details['url']
        products = scrape_extime_perfumes(base_url, threads=optimal_threads)
        
        if products:
            # Initialize filtered_products
            filtered_products = [p for p in products if p.get('brand') and p.get('name')]
            print(f"Filtered out {len(products) - len(filtered_products)} invalid products")
            all_collected_products.extend(filtered_products)
        else:
            print(f"No products scraped for {category}")
    
    # Save results - removed JSON-related code, only keeping CSV
    if all_collected_products:
        # Final cleanup of the data before saving
        all_collected_products = postprocess_product_data(all_collected_products)
        
        base_filename = os.path.join(output_dir, 'extime_products.csv')
        save_to_csv(all_collected_products, base_filename)
        print(f"Scraped total of {len(all_collected_products)} products from all categories.")
    else:
        print("No products were scraped from any category.")

if __name__ == "__main__":
    main()