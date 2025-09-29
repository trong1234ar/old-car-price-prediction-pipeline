import re
import os
import pandas as pd
from typing import List
from .base_crawler import BaseGeneralCrawler
from .car_dao import Car


class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str = "https://bonbanh.com/", additional_url: str ="ha-noi/oto/", swap_page: str="page,", limit: int = 100):
        super().__init__(base_url, additional_url, swap_page, limit)
    
    def _get_hrefs(self, tree) -> List[str]:
        try:
            hrefs = tree.xpath("//li[@class='car-item row1']/a/@href") + tree.xpath("//li[@class='car-item row2']/a/@href")
            hrefs_full = [self.base_url + href for href in hrefs]
            return hrefs_full
        except Exception as e:
            print(f"Error getting hrefs: {e}")
            return []

    def _get_prices(self, tree) -> List[int]:
        try:
            prices = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb3']/b/@content") + tree.xpath("//li[@class='car-item row2']/a/div[@class='cb3']/b/@content")
            for i in range(len(prices)):
                prices[i] = int(prices[i])
            return prices
        except Exception as e:
            print(f"Error getting prices: {e}")
            return []

    def _get_ids(self, tree) -> List[str]:
        try:
            ids = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb5']/span[@class='car_code']/text()") + tree.xpath("//li[@class='car-item row2']/a/div[@class='cb5']/span[@class='car_code']/text()")
            return ids
        except Exception as e:
            print(f"Error getting ids: {e}")
            return []    
    
    def _format_info(self, info):
        for i in range(len(info)):
            info[i] = info[i].strip()
            if i in {0, 9, 10}:
                info[i] = int(re.search(r'\d+', info[i].replace('.', '')).group())
        return info
    
    def _get_detailed_info(self, tree) -> dict:
        try:
            keys = ['year', 'status', 'kilometers', 'origin', 'type_car', 'gear', 'engine', 'color', 'interior_color', 'seats', 'doors', 'transmission']
            car_info = {}
            info = self._format_info(tree.xpath("//span[@class='inp']/text()"))
            car_info = dict(zip(keys, info))
            car_info['brand'] = tree.xpath("//span[@itemprop='name']/strong/text()")[0]
            car_info['name_car'] = tree.xpath("//span[@itemprop='name']/strong/text()")[1]
            car_info['pulished_date'] = re.search(r'\d+/\d+/\d+', tree.xpath("//div[@class='notes']/text()")[0].strip()).group()
            car_info['andress'] = tree.xpath("//div[@class='contact-txt']/text()")[4].strip().removeprefix("Địa chỉ: ").strip()
            print("Got detailed info successfully")
            return car_info
        except Exception as e:
            print(f"Error getting detailed info: {e}")
            return {}

def save_to_csv(cars: List[Car], filename: str = "data\\raw_cars.csv"):
    # convert list Car -> DataFrame
    df = pd.DataFrame([car.dict() for car in cars])
    
    if os.path.exists(filename):
        # nếu file tồn tại thì append, không ghi header
        df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')
        print(f"Appended {len(df)} rows vào {filename}")
    else:
        # nếu chưa có file thì tạo mới + header
        df.to_csv(filename, mode='w', header=True, index=False, encoding='utf-8-sig')
        print(f"Created {filename} với {len(df)} rows")

if __name__ == "__main__":
    crawler = BonBanhCrawler(limit=int(input("Enter limit (-1 for no limit): ")))
    cars = crawler.crawl_all_cars()
    # Save to CSV if existed
    save_to_csv(cars)
    
    print(f"Tổng số xe crawled: {len(cars)}")
    print(cars[0].id, cars[0].href, cars[0].price)