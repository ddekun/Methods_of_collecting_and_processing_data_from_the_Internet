import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='_1IHWd _6Nb0L _37aW8 _2qMLS f-test-button-dalshe f-test-link-Dalshe']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//span[@class='_3y3l6 z4PWH _2Rwtu']//@href").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)

    def parse_vacancy(self, response: HtmlResponse):
        name = response.css("h1::text").get()
        salary = response.xpath("//span[@class='_2eYAG _3y3l6 z4PWH t0SHb']/text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
