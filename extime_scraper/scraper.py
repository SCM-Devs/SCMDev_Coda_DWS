"""
Main scraping module for Extime website.
"""

import re
import time
import random
import concurrent.futures
from datetime import datetime
import sys
from pathlib import Path

# Add the parent directory to sys.path if this module is run directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import from the package
from extime_scraper.http_utils import get_session
from extime_scraper.parser_utils import parse_html
from extime_scraper.product_scraper import extract_product_info, get_cached_product_details
from extime_scraper.categories import is_cave_category

def scrape_extime_perfumes(base_url, max_products=None, threads=5):
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
        time.sleep(random.uniform(1, 2))
        
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
                    page_cache.pop(next(iter(page_cache)))
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = parse_html(response_text)
        
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

    batch_size = min(100, max(5, len(all_products) // threads))
    
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
    
    return products_with_details
