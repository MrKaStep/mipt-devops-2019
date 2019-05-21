import os
import logging
import time
import unicodedata
import graphyte

from pyvirtualdisplay import Display
from selenium import webdriver
from bs4 import BeautifulSoup

logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'https://www.moex.com/ru/issue.aspx?code=YNDX'

GRAPHITE_HOST = os.environ['GRAPHITE_HOST']


def parse_yandex_page(page):

    current_block = page.findAll('li', {'class': 'last'})[0]
    return float(current_block.text.replace(' ', '').replace(',', '.'))


def send_metrics(value):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='stocks')
    sender.send("YNDX", value)


def chrome_example():
    display = Display(visible=0, size=(800, 600))
    display.start()
    logging.info('Initialized virtual display..')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': os.getcwd(),
        'download.prompt_for_download': False,
    })
    logging.info('Prepared chrome options..')

    browser = webdriver.Chrome(chrome_options=chrome_options)
    logging.info('Initialized chrome browser..')

    browser.get(BASE_URL)
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    metric = parse_yandex_page(soup)
    logging.info(f'Got value: {metric}')
    send_metrics(metric)


    logging.info('Accessed %s ..', BASE_URL)

    logging.info('Page title: %s', browser.title)

    browser.quit()
    display.stop()


if __name__ == '__main__':
    chrome_example()
