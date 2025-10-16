from abc import ABC, abstractmethod
from typing import List
import logging
import time

import pandas as pd
from tqdm import tqdm

from src.crawler.car_dto import Car
from src.crawler.utils import get_tree_from_url, get_raw_data, cars_to_df
from src.comparer.data_comparer import DataComparer

class BaseGeneralCrawler(ABC):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int, config):        
        self.base_url = base_url
        self.additional_url = additional_url
        self.swap_page = swap_page
        self.limit = limit
        self.config = config

        self.cars: List[Car] = []
        self.new_cars = []
        self.old_data = get_raw_data(self.config['data']['raw'])
        self.comparer = None
    
    def crawl_search_page(self):
        main_url = self.base_url + self.additional_url
        current_page = 1
        while True:
            search_url = main_url + self.swap_page + str(current_page)
            search_tree = get_tree_from_url(search_url)

            for _ in range(3):
                if search_tree is None:
                    self.logger.warning(f"Failed to get tree from url: {search_url}. Retry in 20 secs.")
                    time.sleep(20)
                    search_tree = get_tree_from_url(search_url)
                else: 
                    break
            else:
                self.logger.warning(f"Failed to get tree from url: {search_url}.")
                time.sleep(20)
                continue

            hrefs = self._get_hrefs(search_tree)
            prices = self._get_prices(search_tree)
            ids = self._get_ids(search_tree)

                
            if search_tree is None or len(hrefs) == 0 or len(prices) == 0 or len(ids) == 0:
                self.logger.info(f"No more data found on page {current_page}. Stopping crawl.")
                break

            if current_page == 1:
                print(search_url)
                last_url, last_page = self._get_last_page(search_tree)

            for href, price, id in zip(hrefs, prices, ids):
                car = {'id': id, 'href': href, 'price': price}
                car['updated_at'] = self.config['TODAY']
                self.cars.append(Car(**car))

            if len(self.cars) % 100 == 0:
                self.logger.info(f"Crawled {len(self.cars)} cars")

            if current_page >= self.limit and self.limit != -1:
                break
            elif current_page >= last_page or search_url == last_url:
                break
            else:
                current_page += 1
        self.logger.info("Complete crawl search page")
        
    def _compare_data(self):
        new_ids = [car.id for car in self.cars]
        self.comparer = DataComparer()
        self.comparer.compare(self.old_data['id'].values, new_ids)
        
    def update_data(self):
        self._compare_data()
        summary = self.comparer.summary
        # update intersection car
        self.old_data.loc[self.old_data['id'].isin(summary["intersection"]), 'updated_at'] = self.config['TODAY']
        # update deleted car
        self.old_data.loc[(self.old_data['id'].isin(summary["deleted"])) & (self.old_data['deleted_at'].isna()), 'deleted_at'] = self.config['TODAY']
        # update created car
        search_page_df = cars_to_df(self.cars)
        new_search_df = search_page_df[search_page_df['id'].isin(summary["created"])]
        self.old_data = pd.concat([self.old_data, new_search_df], ignore_index=True)
        
    def crawl_cars_detail(self):
        summary = self.comparer.summary
        self.logger.info(f"Found {len(summary['created'])} new cars")

        for car in tqdm(self.cars):
            if car.id in summary["created"]:
                detail_tree = get_tree_from_url(car.href)
                for _ in range(3):
                    if detail_tree is None:
                        self.logger.warning(f"Failed to get tree from url: {car.href}. Retry in 20 secs.")
                        time.sleep(20)
                        detail_tree = get_tree_from_url(car.href)
                    else: 
                        break
                else:
                    self.logger.warning(f"Failed to get tree from url: {car.href}.")
                    time.sleep(20)
                    continue
                car_info = {}
                # Extract car specifications
                car_info.update(self._extract_car_specifications(detail_tree))
                # Extract brand and name
                car_info['brand'] = self._extract_brand(detail_tree)
                car_info['name_car'] = self._extract_car_name(detail_tree)
                # Extract published date and address
                car_info['published_date'] = self._extract_published_date(detail_tree)
                car_info['address'] = self._extract_address(detail_tree)
                
                mask = self.old_data['id'] == car.id
                self.old_data.loc[mask, list(car_info.keys())] = list(car_info.values())
                    
    def save_data(self):
        self.old_data.to_csv(self.config['data']['raw'], index=False)
        self.logger.info(f"Saved {len(self.old_data)} cars to {self.config['data']['raw']}")
        self.comparer.save(self.config['log']['summary'])


    @abstractmethod
    def _get_hrefs(self, tree) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def _get_prices(self, tree) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    def _get_ids(self, tree) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def _extract_car_specifications(self, tree) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _extract_brand(self, tree) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def _extract_car_name(self, tree) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def _extract_published_date(self, tree) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def _extract_address(self, tree) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_last_page(self, tree) -> str:
        raise NotImplementedError