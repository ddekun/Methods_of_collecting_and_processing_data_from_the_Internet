from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)

db = client['News']
yandex_news = db.yandex_news


url = 'https://yandex.ru/news'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/102.0.5005.62 Safari/537.36'}

responce = requests.get(url, headers=headers)

dom = html.fromstring(responce.text)

items = dom.xpath('//div[contains(@class, "mg-card mg-card_type_image mg-card_stretching mg-card_flexible-double '
                  'mg-grid__item")]|//div[contains(@class, "mg-card mg-card_flexible-single mg-card_media-fixed-height '
                  'mg-card_type_image mg-grid__item")]')

list_items = []
for item in items:
    item_info = {}
    title = item.xpath('(.//span[contains(@class, "mg-card-source__source")]/a)[position()<6]/text()')
    name = item.xpath('(.//h2/a)[position()<6]/text()')
    link = item.xpath('(.//div/h2/a)[position()<6]/@href')
    date = item.xpath('(.//span[contains(@class, "mg-card-source__time")])[position()<6]/text()')

    item_info['title'] = title[0]
    item_info['name'] = name[0].replace(u'\xa0', ' ')
    item_info['link'] = link
    item_info['date'] = date
    list_items.append(item_info)


pprint(list_items)

yandex_news.insert_many(list_items)

