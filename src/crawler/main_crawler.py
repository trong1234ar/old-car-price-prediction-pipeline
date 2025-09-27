from typing import List

from .base_crawler import BaseGeneralCrawler


class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int):
        super().__init__(base_url, additional_url, swap_page, limit)
    
    def _get_hrefs(self, tree) -> List[str]:
        try:
            hrefs = tree.xpath("//li[@class='car-item row1']/a/@href")
            hrefs_full = [self.base_url + href for href in hrefs]
            return hrefs_full
        except Exception as e:
            print(f"Error getting hrefs: {e}")
            return []

    def _get_prices(self, tree) -> List[int]:
        try:
            prices = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb3']/b/@content")
            return prices
        except Exception as e:
            print(f"Error getting prices: {e}")
            return []

    def _get_ids(self, tree) -> List[str]:
        try:
            ids = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb5']/span[@class='car_code']/text()")
            return ids
        except Exception as e:
            print(f"Error getting ids: {e}")
            return []    