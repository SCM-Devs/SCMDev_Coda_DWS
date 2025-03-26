"""
Main entry point for the Extime scraper application.
"""

import os
import sys
import multiprocessing
from pathlib import Path

# Add the parent directory to sys.path to allow module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now we can import from the package
from extime_scraper.scraper import scrape_extime_perfumes
from extime_scraper.categories import CATEGORIES
from extime_scraper.data_processing import save_to_csv, postprocess_product_data

def main():
    """Main function with optimized execution flow"""
    # Chemin vers le répertoire "extime_scraper" lui-même
    output_dir = os.path.dirname(os.path.abspath(__file__))
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
            
            for product in filtered_products:
                product['dimensions'] = ''
                
            all_collected_products.extend(filtered_products)
        else:
            print(f"No products scraped for {category}")
    
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
