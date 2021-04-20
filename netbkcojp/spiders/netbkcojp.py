import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from netbkcojp.items import Article


class netbkcojpSpider(scrapy.Spider):
    name = 'netbkcojp'
    start_urls = ['https://www.netbk.co.jp/contents/company/press/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_year, dont_filter=True)

        years = response.xpath('//ul[@class="m-lineLink-center"]//a/@href').getall()
        yield from response.follow_all(years, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//dd/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="m-txtAreaR"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="m-contentsWrap"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '<' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
