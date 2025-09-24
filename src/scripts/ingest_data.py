from __future__ import annotations
import random

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

from src.scripts.utils import cars_to_df
from src.crawler.main_crawler import BonBanhCrawler



def run(config=None):
    # Hard code config
    temp_config = {
        "limit": 100,
        "raw_dir": r"D:\Code\old-car-price-prediction\data\raw"
    }
    config = temp_config
    # Crawling
    crawler = BonBanhCrawler(limit=config["limit"])
    cars = crawler.crawl_all_cars()
    # Save to raw
    raw_dir = Path(config["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    data = cars_to_df(cars)
    train, test = train_test_split(data, test_size=0.2, random_state=42)
    train.to_csv(raw_dir / "train.csv", index=False)
    test.to_csv(raw_dir / "test.csv", index=False)
    # Log to mlflow
    print(f"[ingest_data] Wrote {len(train)} rows -> {raw_dir / 'train.csv'}")
    print(f"[ingest_data] Wrote {len(test)} rows -> {raw_dir / 'test.csv'}")

if __name__ == "__main__":
    run()
