import re
import os
import yaml
import pandas as pd
from typing import List
from .base_crawler import BaseGeneralCrawler
from .car_dao import Car

with open("./configs/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str = "https://bonbanh.com/", additional_url: str ="ha-noi/oto/", swap_page: str="page,", limit: int = 100):
        super().__init__(base_url, additional_url, swap_page, limit, config)
    
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
            car_info = {}
            try:
                dict_map = {
                    'Năm sản xuất':'year',
                    'Tình trạng':'status',
                    'Số Km đã đi':'kilometers',
                    'Xuất xứ':'origin',
                    'Kiểu dáng':'type_car',
                    'Hộp số':'gear',
                    'Động cơ':'engine',
                    'Màu ngoại thất':'color',
                    'Màu nội thất':'interior_color',
                    'Số chỗ ngồi':'seats',
                    'Số cửa':'doors',
                    'Dẫn động':'transmission'
                }
                keys = tree.xpath("//label[@for='mail']/text()")
                for i in range(len(keys)):
                    keys[i] = keys[i].strip().replace(":","")
                
                values = self._format_info(tree.xpath("//span[@class='inp']/text()"))
                info = dict(zip(keys, values))
                
                for k, v in dict_map.items():
                    car_info[v] = info.get(k, None)
            
            except Exception as e:
                print(f"Error getting detailed info: {e}")
            
            try:
                car_info['brand'] = tree.xpath("//span[@itemprop='name']/strong/text()")[0]
            except:
                car_info['brand'] = None
            
            try:
                car_info['name_car'] = tree.xpath("//span[@itemprop='name']/strong/text()")[1]
            except:
                car_info['name_car'] = None
            
            try:
                car_info['published_date'] = re.search(r'\d+/\d+/\d+', tree.xpath("//div[@class='notes']/text()")[0].strip()).group()
            except:
                car_info['published_date'] = None
            
            try:
                car_info['address'] = tree.xpath("//div[@class='contact-txt']/text()")[4].strip().removeprefix("Địa chỉ: ").strip()
            except:
                car_info['address'] = None
            
            print("Got detailed info successfully")
            return car_info
        except Exception as e:
            print(f"Error getting detailed info: {e}")
            return {}

if __name__ == "__main__":
    crawler = BonBanhCrawler(limit=int(input("Enter limit (-1 for no limit): ")))
    crawler.get_car_hrefs()
    crawler.crawl_all_cars()
    