from typing import List

from .base_crawler import BaseGeneralCrawler


class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str = "https://bonbanh.com", additional_url: str ="/oto-cu-da-qua-su-dung", swap_page: str="/page,", limit: int = 100):
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

if __name__ == "__main__":
    crawler = BonBanhCrawler(limit=10)
    cars = crawler.crawl_all_cars()
    print(cars[0].id, cars[0].href, cars[0].price)