from __future__ import annotations
import random
import time

from pathlib import Path
import pandas as pd

from configs.config import load_config
from src.scripts.utils import cars_to_df
from src.crawler.main_crawler import BonBanhCrawler



def run():
    start = time.time()
    config = load_config()

    # Crawling overview
    crawler_config = config["crawler"]["overview"]
    crawler = BonBanhCrawler(**crawler_config)
    crawler.crawl_search_page()
    crawler.crawl_car_detail()
    crawler.save_data()
    
    end = time.time()
    print(f"Total time: {end - start:.2f} seconds")
if __name__ == "__main__":
    run()
