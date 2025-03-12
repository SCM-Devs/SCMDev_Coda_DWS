import requests
from bs4 import BeautifulSoup

def scrape_extime():
    url = "https://www.extime.com"
    response = requests.get(url)
    
    print(f"Statut de la réponse : {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="product")
        
        print(f"Nombre de produits trouvés : {len(products)}")
        
        products_list = []
        
        for product in products:
            try:
                name = product.find('h2', class_='product-name').get_text(strip=True)
                brand = product.find('span', class_='product-brand').get_text(strip=True)
                volume = product.find('span', class_='product-volume').get_text(strip=True)
                product_type = product.find('span', class_='product-type').get_text(strip=True)
                image = product.find('img')['src']
                
                products_list.append({
                    'name': name,
                    'Marque': brand,
                    'Volume': volume,
                    'Type': product_type,
                    'Image': image
                })
            except AttributeError as e:
                print(f"Erreur lors de l'extraction des données : {e}")
        
        return products_list
    else:
        print(f"Erreur lors de la récupération de la page : {response.status_code}")
        return None

if __name__ == "__main__":
    products = scrape_extime()
    if products:
        for product in products:
            print(product)
    else:
        print("Aucun produit trouvé.")