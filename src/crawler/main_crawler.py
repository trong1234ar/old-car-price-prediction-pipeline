from typing import List
import re

from src.crawler.base_crawler import BaseGeneralCrawler


class BonBanhCrawler(BaseGeneralCrawler):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int, config, logger):
        super().__init__(base_url, additional_url, swap_page, limit, config)
        self.logger = logger
        
            
    def _get_hrefs(self, tree) -> List[str]:
        try:
            hrefs = tree.xpath("//li[@class='car-item row1']/a/@href") \
                  + tree.xpath("//li[@class='car-item row2']/a/@href")
            hrefs_full = [self.base_url + '/' + href for href in hrefs]
            return hrefs_full
        except Exception as e:
            self.logger.info(f"Error getting hrefs: {e}")
            return []

    def _get_prices(self, tree) -> List[int]:
        try:
            prices = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb3']/b/@content")\
                   + tree.xpath("//li[@class='car-item row2']/a/div[@class='cb3']/b/@content")
            return prices
        except Exception as e:
            self.logger.info(f"Error getting prices: {e}")
            return []

    def _get_ids(self, tree) -> List[str]:
        try:
            ids = tree.xpath("//li[@class='car-item row1']/a/div[@class='cb5']/span[@class='car_code']/text()") \
                + tree.xpath("//li[@class='car-item row2']/a/div[@class='cb5']/span[@class='car_code']/text()")
            return ids
        except Exception as e:
            self.logger.info(f"Error getting ids: {e}")
            return []

    def _format_info(self, info):
        """Formats and cleans the extracted information values."""
        for i in range(len(info)):
            info[i] = info[i].strip()
            if i in {0, 9, 10}:
                info[i] = int(re.search(r'\d+', info[i].replace('.', '')).group())
        return info

    def _get_field_mapping(self) -> dict:
        """Returns the mapping from Vietnamese field names to English keys."""
        return {
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
    
    def _extract_car_specifications(self, tree) -> dict:
        """Extracts car specifications from the detail page."""
        try:
            dict_map = self._get_field_mapping()
            keys = tree.xpath("//label[@for='mail']/text()")
            for i in range(len(keys)):
                keys[i] = keys[i].strip().replace(":","")
            
            values = self._format_info(tree.xpath("//span[@class='inp']/text()"))
            info = dict(zip(keys, values))
            
            car_specs = {}
            for k, v in dict_map.items():
                car_specs[v] = info.get(k, None)
            
            return car_specs
        except Exception as e:
            self.logger.info(f"Error extracting car specifications: {e}")
            return {}
    
    def _extract_brand(self, tree) -> str:
        """Extracts the car brand from the detail page."""
        try:
            return tree.xpath("//span[@itemprop='name']/strong/text()")[0]
        except Exception as e:
            self.logger.info(f"Error extracting brand: {e}")
            return None
    
    def _extract_car_name(self, tree) -> str:
        """Extracts the car name from the detail page."""
        try:
            return tree.xpath("//span[@itemprop='name']/strong/text()")[1]
        except Exception as e:
            self.logger.info(f"Error extracting car name: {e}")
            return None
    
    def _extract_published_date(self, tree) -> str:
        """Extracts the published date from the detail page."""
        try:
            notes_text = tree.xpath("//div[@class='notes']/text()")[0].strip()
            return re.search(r'\d+/\d+/\d+', notes_text).group()
        except Exception as e:
            self.logger.info(f"Error extracting published date: {e}")
            return None
    
    def _extract_address(self, tree) -> str:
        """Extracts the seller's address from the detail page."""
        try:
            add = tree.xpath("//div[@class='contact-txt']/text()")
            address = next((item for item in add if "Địa chỉ:" in item), "").strip().replace("Địa chỉ: ", "")
            return address
        except Exception as e:
            self.logger.info(f"Error extracting address: {e}")
            return None
    
    def _get_last_page(self, tree) -> str:
        try:
            url = tree.xpath('//*[@id="s-list-car"]/div/div[2]/div[2]/div/span[8]/@url')[0]
            page = int(re.sub('[^0-9]', '', url))
            return url, page
        except Exception as e:
            self.logger.info(f"Error getting last page: {e}")
            return None, None