import datetime
from abc import ABC, abstractmethod
from typing import List

from .car_dao import Car
from .utils import get_tree_from_url


class BaseGeneralCrawler(ABC):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int):
        self.base_url = base_url
        self.additional_url = additional_url
        self.swap_page = swap_page
        self.limit = limit
    
    def crawl_all_cars(self) -> List[Car]:
        main_url = self.base_url + self.additional_url
        cars = []
        current_page = 1
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        
        # If limit is -1, crawl until no more data is available
        if self.limit == -1:
            while True:
                crawl_url = main_url + self.swap_page + str(current_page)
                tree = get_tree_from_url(crawl_url)
                
                # Get data from current page
                hrefs = self._get_hrefs(tree)
                prices = self._get_prices(tree)
                ids = self._get_ids(tree)
                
                # If no data found on this page, stop crawling
                if not tree or not hrefs or not prices or not ids or len(hrefs) == 0:
                    print(f"No more data found on page {current_page}. Stopping crawl.")
                    break
                
                # Add cars from current page
                for href, price, id in zip(hrefs, prices, ids):
                    tree_ = get_tree_from_url(href)
                    
                    if tree_ is None:
                        print(f"Skipping car {id} with href {href} due to failed page load.")
                        continue
                    
                    car = self._get_detailed_info(tree_)
                    car.update({'id': id, 'href': href, 'price': price, 'crawled_date': date})
                    
                    cars.append(Car(**car))
                
                print(f"Crawled {len(cars)} cars (page {current_page})")
                current_page += 1
        else:
            # Original behavior: crawl up to specified limit
            for current_page in range(1, self.limit + 1):
                crawl_url = main_url + self.swap_page + str(current_page)
                tree = get_tree_from_url(crawl_url)
                hrefs = self._get_hrefs(tree)
                prices = self._get_prices(tree)
                ids = self._get_ids(tree)
                for href, price, id in zip(hrefs, prices, ids):
                    cars.append(Car(id=id, href=href, price=price))
                print(f"Crawled {len(cars)} cars")
        
        return cars

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
