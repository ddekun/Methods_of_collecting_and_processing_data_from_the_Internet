import scrapy
from scrapy.http import HtmlResponse
from castoramaparser.items import CastoramaParserItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    start_urls = ['https://www.castorama.ru/flooring/laminate']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='product-card__img-link']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)


    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=CastoramaParserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//li[contains(@class, 'top-slide swiper-slide')]/div/img/@data-src")
        loader.add_xpath('price', "(//span[contains(@id, 'product-price')]/span/span/span)[1]/text()")
        loader.add_value('url', response.url)
        yield loader.load_item()

        # name = response.xpath("//h1/text()").get()
        # photos = response.xpath("//li[contains(@class, 'top-slide swiper-slide')]/div/img/@data-src").getall()
        # url = response.url
        # price = response.xpath("(//span[contains(@id, 'product-price')]/span/span/span)[1]/text()").get()
        # yield CastoramaParserItem(name=name, photos=photos, url=url, price=price)

