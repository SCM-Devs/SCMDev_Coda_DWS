class Product:
    def __init__(self, id, brand, name, categorie, volume, scraped_date, net_weight, image_url, materiaux, nom_d_origine, dimensions, status):
        self.id = id
        self.brand = brand
        self.name = name
        self.categorie = categorie
        self.volume = volume
        self.scraped_date = scraped_date
        self.net_weight = net_weight
        self.image_url = image_url
        self.materiaux = materiaux
        self.nom_d_origine = nom_d_origine
        self.dimensions = dimensions
        self.status = status
        
    def convert_to_dic(self):
        return {
            'id' : self.id,
            'brand' : self.brand,
            'name' : self.name,
            'categorie' : self.categorie,
            'volume' : self.volume,
            'scraped_date' : self.scraped_date,
            'net_weight' : self.net_weight,
            'image_url' : self.image_url,
            'materiaux' : self.materiaux,
            'nom_d_origine' : self.nom_d_origine,
            'dimensions' : self.dimensions,
            'status' : self.status
        }
    
    @classmethod
    def from_csv_row(cls, row):
        return cls (
            row['id'],
            row['brand'], 
            row['name'],
            row['categorie'],
            row['volume'],
            row['scraped_date'],
            row['net_weight'],
            row['image_url'],
            row['materiaux'],
            row['nom_d_origine'],
            row['dimensions'],
            row['status']
        )
    