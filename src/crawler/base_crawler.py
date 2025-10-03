from abc import ABC, abstractmethod
from typing import List
from itertools import count

from .car_dao import Car
from .utils import get_tree_from_url

class BaseGeneralCrawler(ABC):
    def __init__(self, base_url: str, additional_url: str, swap_page: str, limit: int, config):
        self.base_url = base_url
        self.additional_url = additional_url
        self.swap_page = swap_page
        self.limit = limit
        self.cars: List[Car] = []

        try:
            self.old_data = pd.read_csv(config['data']['raw'])
        except:
            self.old_data = pd.DataFrame()
    
    def crawl_search_page(self) -> List[Car]:
        main_url = self.base_url + self.additional_url
        current_page = 1

        while True:
            search_url = main_url + self.swap_page + str(current_page)
            search_tree = get_tree_from_url(search_url)
            hrefs = self._get_hrefs(search_tree)
            prices = self._get_prices(search_tree)
            ids = self._get_ids(search_tree)

            # Stop only for unlimited mode when no more data
            if not search_tree or not hrefs or not prices or not ids or len(hrefs) == 0:
                print(f"No more data found on page {current_page}. Stopping crawl.")
                break

            for href, price, id in zip(hrefs, prices, ids):
                if id in self.old_data['id'].values:
                    self
                car = {'id': id, 'href': href, 'price': price}
                cars.append(Car(**car))

            print(f"Crawled {len(cars)} cars")

            if current_page >= self.limit and self.limit != -1:
                break
            else:
                current_page += 1

        return cars

    def crawl_car_detail():
        pass

    @abstractmethod
    def _get_hrefs(self, tree) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def _get_prices(self, tree) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    def _get_ids(self, tree) -> List[str]:
        raise NotImplementedError