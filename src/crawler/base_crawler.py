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
        