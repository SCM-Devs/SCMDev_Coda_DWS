class Product:
    def __init__(self, brand, name, categorie, volume, scraped_date, net_weight):
        self.brand  = brand
        self.name  = name
        self.categorie  = categorie
        self.volume  = volume
        self.scraped_date  = scraped_date
        self.net_weight  = net_weight

    def convert_to_dic(self):
        return {
            'brand' : self.brand,
            'name' : self.name,
            'categorie' : self.categorie,
            'volume' : self.volume,
            'scraped_date' : self.scraped_date,
            'net_weight' : self.net_weight
        }
    
    @classmethod
    def from_csv_row(cls, row):
        return cls (
            row['brand'], 
            row['name'],
            row['categorie'],
            row['volume'],
            row['scraped_date'],
            row['net_weight']
        )
    