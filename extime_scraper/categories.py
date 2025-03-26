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
    return CATEGORIES.get(category, {}).get('url')

def is_cave_category(base_url):
    return any(category in base_url for category in ['champagne', 'spiritueux', 'vin'])

def get_all_categories():
    return CATEGORIES.keys()
