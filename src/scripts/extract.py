from __future__ import annotations
import random
import time

from pathlib import Path
import pandas as pd

from configs.config import load_config
from src.crawler.main_crawler import BonBanhCrawler
from src.logger.logger import get_logger


def run():
    start = time.time()
    config = load_config()
    logger = get_logger("Crawler", "INFO", "./log/crawler.log")
    # Crawling overview
    crawler_config = config["crawler"]["overview"]
    crawler = BonBanhCrawler(**crawler_config, config=config, logger=logger)
    crawler.crawl_search_page()
    crawler.update_data()
    crawler.save_data()
    crawler.crawl_cars_detail()
    crawler.save_data()
    
    end = time.time()
    logger.info(f"Total time: {end - start:.2f} seconds")


if __name__ == "__main__":
    run()
