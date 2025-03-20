import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import random

class Scraper:
    BASE_URL = "https://www.extime.com/fr/paris/shopping"
    CATEGORIES = {
        'parfum': f"{BASE_URL}/beaute/parfum",
        'cave': f"{BASE_URL}/cave"
    }
    # URL à filtrer
    ANIMATION_GIF_URL = "https://stproadpmkpshare01.blob.core.windows.net/extime/assets/extime_hostedby_parisaeroport_anim_a4b5fada25.gif"
    
    def __init__(self, max_concurrent_requests=10):
        # Limite le nombre de requêtes simultanées pour ne pas surcharger le serveur.
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        # S'assurer que lxml est installé au démarrage
        try:
            import lxml
            self.parser = "lxml"
            print("Utilisation du parser lxml pour des performances optimales.")
        except ImportError:
            print("WARNING: Le parser lxml n'est pas installé. Installation avec: pip install lxml")
            print("Utilisation du parser html.parser (plus lent).")
            self.parser = "html.parser"
    
    async def fetch(self, session, url):
        async with self.semaphore:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    return await response.text()
            except Exception as e:
                print(f"Erreur lors de la récupération de {url} : {e}")
                return None

    async def scrape_product_details(self, session, product_url):
        """Récupère des détails supplémentaires depuis la page produit."""
        html = await self.fetch(session, product_url)
        if not html:
            return {}
        soup = BeautifulSoup(html, self.parser)  # Utilisation du parser optimisé
        volume = soup.select_one('span[data-testid="volume"]')
        net_weight = soup.select_one('span[data-testid="net-weight"]')
        return {
            "volume": volume.get_text(strip=True) if volume else None,
            "net_weight": net_weight.get_text(strip=True) if net_weight else None
        }
    
    def is_valid_product(self, product_data):
        """Vérifie si un produit est valide pour être inclus dans les résultats"""
        # Filtrer les produits sans marque ou sans nom
        if not product_data.get("brand") or not product_data.get("name"):
            return False
            
        # Filtrer les produits avec l'URL de l'image d'animation
        if product_data.get("image_url") == self.ANIMATION_GIF_URL:
            return False
            
        return True
    
    async def scrape_category(self, session, category_url):
        products = []
        page = 1
        base_url = category_url.split('?')[0]
        while True:
            print(f"Scraping de la page {page} de {category_url}...")
            # Sur la première page, on utilise l'URL d'origine
            url = category_url if page == 1 else f"{base_url}?p={page}"
            html = await self.fetch(session, url)
            if not html:
                break
            
            # Utilisation du parser lxml pour une analyse plus rapide
            soup = BeautifulSoup(html, self.parser)
            product_elements = soup.find_all('a', class_='relative')
            if not product_elements:
                break

            # Préparation des tâches asynchrones pour récupérer les détails produits
            tasks = []
            product_data = []
            
            # Utilisation de list comprehension et de générateurs pour optimiser la performance
            for product in product_elements:
                product_url = product.get('href')
                if not product_url.startswith("http"):
                    product_url = f"https://www.extime.com{product_url}"
                
                # Création d'une tâche asynchrone
                tasks.append(asyncio.create_task(self.scrape_product_details(session, product_url)))
                
                # Récupération des informations de base du produit avec des sélecteurs optimisés
                brand_el = product.select_one('h3.relative span[title]')
                name_el = product.select_one('h4.relative span.line-clamp-3')
                image_el = product.find('img')
                
                # Extraction des données avec une meilleure gestion des valeurs null
                brand = brand_el.get_text(strip=True) if brand_el else ""
                name = name_el.get_text(strip=True) if name_el else ""
                image_url = image_el.get('src') if image_el else ""
                
                product_data.append({
                    "category": category_url.split('/')[-1],
                    "brand": brand,
                    "name": name,
                    "url": product_url,
                    "image_url": image_url,
                    "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # Récupération concurrente des détails produits - optimisée
            details_list = await asyncio.gather(*tasks)
            
            # Filtrer les produits valides avant de les ajouter à la liste
            # Utiliser une liste en compréhension pour une meilleure performance
            valid_products = []
            for i, details in enumerate(details_list):
                product_data[i]["volume"] = details.get("volume")
                product_data[i]["net_weight"] = details.get("net_weight")
                
                # N'ajouter que les produits valides
                if self.is_valid_product(product_data[i]):
                    valid_products.append(product_data[i])
            
            products.extend(valid_products)
            
            # Vérifie la présence d'un bouton pour charger plus de produits
            load_more_button = soup.select_one('button.whitespace-no-wrap[aria-label="Afficher plus de produits"]')
            if not load_more_button:
                print("Bouton 'Afficher plus de produits' introuvable. Fin de la pagination.")
                break
            
            page += 1
            # Délai réduit mais raisonnable pour ne pas surcharger le serveur
            await asyncio.sleep(random.uniform(0.1, 0.3))  # Réduit légèrement le délai pour plus de rapidité
        return products

    async def scrape_all_categories(self):
        all_products = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for category, url in self.CATEGORIES.items():
                tasks.append(asyncio.create_task(self.scrape_category(session, url)))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
        return all_products

    def save_to_csv(self, products, filename):
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "brand", "name", "url", "image_url", "volume", "net_weight", "scraped_date"])
            writer.writeheader()
            writer.writerows(products)
        print(f"{len(products)} produits sauvegardés dans {filepath}")

    async def run(self):
        # Calculer le temps d'exécution pour voir l'amélioration de performance
        start_time = datetime.now()
        products = await self.scrape_all_categories()
        # Filtrage supplémentaire avant la sauvegarde pour s'assurer qu'aucun produit invalide n'a été ajouté
        filtered_products = [p for p in products if self.is_valid_product(p)]
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"Nombre total de produits: {len(products)}")
        print(f"Nombre de produits filtrés: {len(filtered_products)}")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        self.save_to_csv(filtered_products, "extime_products.csv")


if __name__ == "__main__":
    scraper = Scraper(max_concurrent_requests=15)  # Augmenter légèrement le nombre de requêtes concurrentes
    asyncio.run(scraper.run())
