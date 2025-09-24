from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup
from lxml import html

def get_tree_from_url(url: str, headers: Optional[Dict] = None):
    try:
        HEADERS = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        normalized_html = str(soup)
        tree = html.fromstring(normalized_html)
        return tree
    except Exception as e:
        print(f"Error getting tree from url: {e}")
        return None