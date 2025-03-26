"""
HTTP utilities for making requests to the Extime website.
"""

import random
import requests
import time
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

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

def get_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

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

def request_with_retry(url, session=None, retry_count=0, max_retries=3):
    """Make a request with retry logic for 403 errors"""
    if session is None:
        session = get_session()
    else:
        # Update user agent for this request to vary behavior
        session.headers.update({'User-Agent': get_random_user_agent()})
    
    # Add a referer to appear more browser-like
    session.headers.update({'Referer': "https://www.extime.com/fr/paris/shopping"})
    
    try:
        # Add a random delay to mimic human behavior
        delay = random.uniform(0.5, 1.5)
        print(f"Waiting {delay:.1f}s before fetching {url}")
        time.sleep(delay)
        
        response = session.get(url)
        
        # Special handling for 403 errors with exponential backoff
        if response.status_code == 403:
            if retry_count < max_retries:
                wait_time = 2 * (2 ** retry_count) + random.uniform(0, 1)
                print(f"403 Forbidden error. Attempt {retry_count + 1}/{max_retries}. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                
                # Create a fresh session for the retry
                new_session = get_session()
                return request_with_retry(url, new_session, retry_count + 1, max_retries)
            else:
                print(f"Maximum retries reached. Failed to fetch {url}")
                return None
        
        response.raise_for_status()
        return response
        
    except Exception as e:
        print(f"Error making request: {e}")
        return None
