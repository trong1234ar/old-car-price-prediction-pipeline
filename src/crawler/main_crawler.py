from typing import List
import re

from .base_crawler import BaseGeneralCrawler


class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int):
        super().__init__(base_url, additional_url, swap_page, limit)
        
            
    def _get_hrefs(self, tree) -> List[str]:
        try:
            hrefs = tree.xpath("//li[@class='car-item row1']/a/@href")
            hrefs_full = [self.base_url + '/' + href for href in hrefs]
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
            try:
                car_info['brand'] = tree.xpath("//span[@itemprop='name']/strong/text()")[0]
            except:
                car_info['brand'] = None
            try:
                car_info['name_car'] = tree.xpath("//span[@itemprop='name']/strong/text()")[1]
            except:
                car_info['name_car'] = None
            try:
                car_info['pulished_date'] = re.search(r'\d+/\d+/\d+', tree.xpath("//div[@class='notes']/text()")[0].strip()).group()
            except:
                car_info['pulished_date'] = None
            try:
                car_info['andress'] = tree.xpath("//div[@class='contact-txt']/text()")[4].strip().removeprefix("Địa chỉ: ").strip()
            except:
                car_info['andress'] = None
            return car_info
        except Exception as e:
            print(f"Error getting detailed info: {e}")
            return {}