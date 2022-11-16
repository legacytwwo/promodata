import csv
from bs4 import BeautifulSoup
from requests import get, ConnectionError

from time import sleep
from sys import exc_info
from os import path, makedirs

from typing import Optional
from config import get_config
from dataclasses import dataclass

@dataclass
class CategoryInstance:
    parent_id: str
    id: Optional[str] = None
    name: Optional[str] = None

class ParseCategories:
    config = get_config()
    site_url = 'https://zootovary.ru'

    def __init__(self) -> None:
        self.dirs = [self.config.logs_dir, self.config.output_directory]
    
    def parse_categories(self) -> list[str]:
        categories = []
        response = get(self.site_url, headers=self.config.headers)
        if not response.ok:
            for _ in range(self.config.max_retries):
                response = get(self.site_url, headers=self.config.headers)
                sleep(self.config.delay_range_s)
                if response.ok:
                    break
            if not response.ok:
                raise ConnectionError("Max retries")
        soup = BeautifulSoup(response.text, "html.parser")
        parse_data = soup.findAll('a', class_='catalog-menu-icon')
        for category in parse_data:
            categories.append(category['href'])
        return categories
    
    def parse_subcategories(self, categories: list[str]) -> list[CategoryInstance]:
        result = []
        for category in categories:
            response = get(self.site_url+category, headers=self.config.headers)
            sleep(self.config.delay_range_s)
            if not response.ok:
                for _ in range(self.config.max_retries):
                    response = get(self.site_url+category, headers=self.config.headers)
                    sleep(self.config.delay_range_s)
                    if response.ok:
                        break
                if not response.ok:
                    raise ConnectionError("Max retries")
            soup = BeautifulSoup(response.text, "html.parser")
            parse_data = soup.findAll('a', class_='item-depth-1')
            for subcategory in parse_data:
                result.append(CategoryInstance(
                    parent_id=category,
                    id=subcategory['href'],
                    name=subcategory['title']
                ))
        return result

    def get_csv(self, result: list[CategoryInstance]) -> bool:
        with open(f'{self.config.output_directory}/categories.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            header = ['name', 'id', 'parent_id']
            writer.writerow(header)
            ind = -1
            for x in result:
                ind = ind + 1
                row = [x.name, x.id, x.parent_id]
                writer.writerow(row)
        return True
    
    def create_dirs_if_not_exist(self, dirs: list[str]):
        for dir in dirs:
            if not path.exists(dir):
                makedirs(dir)
    
    def write_logs(self, log: str):
        print(log)
        with open(f'{self.config.logs_dir}/logs.txt', 'a') as file:
            file.write(log+'\n')
    
    def parse_process(self):
        for _ in range(self.config.restart.restart_count):
            try:
                self.create_dirs_if_not_exist(self.dirs)
                self.write_logs("START")
                categories = self.parse_categories()
                self.write_logs("FINISH PARSE CATEGORIES")
                result = self.parse_subcategories(categories)
                self.write_logs("FINISH PARSE SUBCATEGORIES")
                file = self.get_csv(result)
                if file:
                    self.write_logs("FINISH")
                    break
            except Exception as error:
                traceback = exc_info()[2]
                fname = path.split(traceback.tb_frame.f_code.co_filename)[1]
                error_status = f'File: {fname}; Line: {traceback.tb_lineno}; Error: {error}'
                self.write_logs(error_status)
                sleep(self.config.restart.interval_m)