from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd

from src.crawler.car_dto import Car


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

def get_raw_data(file_path: str) -> pd.DataFrame:
        try:
            old_data = pd.read_parquet(file_path)
        except:
            try:
                old_data = pd.read_csv(file_path)
            except:
                old_data = pd.DataFrame(columns=list(Car.model_fields.keys()))
        return old_data

def cars_to_df(cars: List[Car]) -> pd.DataFrame:
    df = pd.DataFrame([car.dict() for car in cars])
    return df