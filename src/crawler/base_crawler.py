import datetime
import time
import pandas as pd
from itertools import count
from abc import ABC, abstractmethod
from typing import List

from .car_dao import Car
from .utils import get_tree_from_url

class BaseGeneralCrawler(ABC):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int, config):
        self.base_url = base_url
        self.additional_url = additional_url
        self.swap_page = swap_page
        self.limit = limit
        self.config = config
        self.cars:List[Car] = []
        self.new_cars = []
        
        try:
            self.old_data = pd.read_csv(config['data']['raw'])
        except:
            self.old_data = pd.DataFrame()
    
    def get_detail(self, car:Car) -> Car:
        try:
            href = car.href
            id = car.id
            price = car.price
            crawl_date = car.updated_at
            
            tree_ = get_tree_from_url(href)
            print(f"Processing car {id} with href {href}")
            
            if tree_ is None:
                print(f"Skipping car {id} with href {href} due to failed page load.")
            
            car_ = self._get_detailed_info(tree_)
            car_.update({
                'id': id,
                'href': href,
                'price': price,
                'updated_at': crawl_date
            })
            
            return Car(**car_)
        except Exception as e:
            print(f"<!> Error processing car {id} with href {href}: {e} <!>")
    
    def get_car_hrefs(self) -> List[Car]:
        main_url = self.base_url + self.additional_url
        current_page = 1
        date = str(datetime.datetime.now().strftime("%d/%m/%Y"))
        
        # If limit is -1, crawl until no more data is available
        if self.limit == -1:
            while True:
                crawl_url = main_url + self.swap_page + str(current_page)
                tree = get_tree_from_url(crawl_url)
                
                # Get data from current page
                hrefs = self._get_hrefs(tree)
                prices = self._get_prices(tree)
                ids = self._get_ids(tree)
                
                for href, price, id in zip(hrefs, prices, ids):
                    car = Car(id=id, href=href, price=price, updated_at=date)
                    self.cars.append(car)
                
                # If no data found on this page, stop crawling
                if not tree or not hrefs or not prices or not ids or len(hrefs) == 0:
                    print(f"No more data found on page {current_page}. Stopping crawl.")
                    break
                time.sleep(30)
        else:
            # Original behavior: crawl up to specified limit
            for current_page in range(1, self.limit + 1):
                crawl_url = main_url + self.swap_page + str(current_page)
                tree = get_tree_from_url(crawl_url)
                hrefs = self._get_hrefs(tree)
                prices = self._get_prices(tree)
                ids = self._get_ids(tree)
                
                for href, price, id in zip(hrefs, prices, ids):
                    car = Car(id=id, href=href, price=price, updated_at=date)
                    self.cars.append(car)
                
                #timeout between pages
                time.sleep(30)
        return self.cars
    
    def crawl_all_cars(self) -> List[Car]:
        # Read file CSV to get existing car IDs
        existing_ids = set()
        try:
            existing_ids = set(self.old_data['id'].astype(str).tolist())
            print(f"Loaded {len(existing_ids)} existing car IDs from CSV.")
            
            for car in self.cars:
                if car.id not in existing_ids:
                    detailed_car = self.get_detail(car)
                    
                    if detailed_car:
                        self.new_cars.append(detailed_car)
                        print(f"Added new car with ID {car.id}")
                else:
                    self.old_data.loc[self.old_data['id'] == car.id, 'updated_at'] = car.updated_at
                    print(f"Car with ID {car.id} already exists. Skipping.")
            # Combine old and new data
            df_new = pd.DataFrame([car.dict() for car in self.new_cars])
            combined_df = pd.concat([self.old_data, df_new], ignore_index=True)
            self.old_data = combined_df
            self.old_data.to_csv(self.config['data']['raw'], index=False, encoding='utf-8-sig')
            print(f"Updated CSV with {len(self.new_cars)} new cars. Total now: {len(self.old_data)}")
        except Exception as e:
            print(f"Error reading existing CSV file: {e}")
            for i in range(len(self.cars)):
                detailed_car = self.get_detail(self.cars[i])
                if detailed_car:
                    self.new_cars.append(detailed_car)
                    print(f"Added new car with ID {self.cars[i].id}")
            
            self.old_data = pd.DataFrame([car.dict() for car in self.new_cars])
            self.old_data.to_csv(self.config['data']['raw'], index=False, encoding='utf-8-sig')

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
    def _get_detailed_info(self, tree) -> dict:
        raise NotImplementedError