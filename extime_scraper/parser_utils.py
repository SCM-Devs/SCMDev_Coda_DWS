"""
Parsing utilities for extracting data from web pages.
"""

import re
from bs4 import BeautifulSoup

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

# Liste de phrases à exclure
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


def parse_html(html_content):
    """Parse HTML content using the best available parser"""
    return BeautifulSoup(html_content, BEST_PARSER)

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
