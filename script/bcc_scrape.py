from bs4 import BeautifulSoup
from selenium import webdriver
import yaml
import requests
import sys
import time


class BccScrape():
    def __init__(self, target_num=None):

        self.browser_head = None
        self.target_num = target_num
        self.rec_num = None
        self.base_url = None
        self.soup = None
        self.driver_path = None
        self.driver = None
        self.rec_field = None
        self.css = None
        self.encoding = None

    def load_settings(self, setting_path):

        with open(setting_path, encoding='utf_8_sig') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)

        self.browser_head = config['browser_head']
        self.base_url = config['base_url']
        self.driver_path = config['driver']
        self.rec_field = config['rec_field']
        self.css = config['css']
        self.encoding = config['encoding']

    def load_search_page(self):

        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(self.driver_path, options=option)
        driver.get(self.base_url + self.target_num + '/')

        self.driver = driver

    def load_scraper(self):

        url = self.base_url + self.target_num + '/'

        html = requests.get(url, headers=self.browser_head)
        html.encoding = self.encoding
        soup = BeautifulSoup(self.driver.page_source, features='lxml')

        self.soup = soup

    def get_rec_items(self):

        withBuy = self.soup.select(self.rec_field)[0]
        withBuy_items = withBuy.find_all('a', class_=self.css)

        url_list = []
        for urls in withBuy_items:
            url_list.append(urls.get('href'))

        url_set = set(url_list)

        item_nums = [url.split('/')[-2] + '\n' for url in url_set]

        self.rec_num = item_nums

    def save_to_csv(self, save_dir):

        save_path = save_dir + '/' + self.target_num + '.csv'

        with open(save_path, mode='w') as fn:
            fn.writelines(self.rec_num)


def start_scrape(scraper, target_num, save_dir):

    try:
        scraper.target_num = target_num
        scraper.load_search_page()
        scraper.load_scraper()
        scraper.get_rec_items()
        scraper.save_to_csv(save_dir)
        time.sleep(30)
    except Exception as e:
        print(e)
        print('no recommendation items')


def main():

    setting_path = sys.argv[1]
    target_items_path = sys.argv[2]
    save_dir = sys.argv[3]

    with open(target_items_path, mode='r') as fn:
        target_num_list = fn.readlines()

    target_num_list_clean = [
        str(target).replace('\n', '') for target in target_num_list
    ]

    scraper = BccScrape()
    scraper.load_settings(setting_path)

    print('start scraping')
    for i, target_num in enumerate(target_num_list_clean):
        print('{}/{}'.format(i + 1, len(target_num_list)))
        print('target: ', target_num)
        start_scrape(scraper, target_num, save_dir)
    print('end scarping')


if __name__ == '__main__':
    main()
