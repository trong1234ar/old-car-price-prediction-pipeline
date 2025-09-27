from __future__ import annotations
import random

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

from configs.config import load_config
from src.scripts.utils import cars_to_df
from src.crawler.main_crawler import BonBanhCrawler



def run():
    config = load_config()
    # Crawling overview
    crawler_config = config["crawler"]["overview"]
    crawler = BonBanhCrawler(**crawler_config)
    cars = crawler.crawl_all_cars()
    new_data = cars_to_df(cars)
    new_data['created_at'] = config["TODAY"]
    new_data['deleted_at'] = pd.NaT
    new_data.to_csv(config["data"]["raw"]["overview"], index=False)
    print("Overview data saved to", config["data"]["raw"]["overview"])
if __name__ == "__main__":
    run()
