# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from lxml import etree
import time
from PCauto import pipelines
from PCauto.items import PCautoTireItem

class PCautoTireSpider(RedisSpider):
    name = 'PCauto_tire'
    index_page = 'http://www.pcauto.com.cn/drivers/tire/'

    pipeline = set([pipelines.TirePipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_nav)

    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//ul[@id="nav"]/li')
        for nav in nav_list[1:]:
            href = nav.xpath('./a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)


    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//div[@class="box list"]//div[@class="pic-txt clearfix"]')
        for article in articles:
            href = article.xpath('./div[@class="txt"]//p[@class="tit blue"]/a/@href')[0]
            yield Request(href, callback=self.get_url)

        page_info = model.xpath('//div[@class="pcauto_page"]')
        if page_info:
            next_page = page_info[0].xpath('./a[@class="next"]')
            if next_page:
                next_page_url = next_page[0].xpath('./@href')[0]
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoTireItem()

        result['category'] = '轮胎'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="guide")
        # nav and aiticle
        if place:
            mark = place.find('span',class_="mark")
            if mark:
                text = mark.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
            crumbs = place.find('div', class_='crumbs')
            if crumbs:
                text = crumbs.get_text().strip().replace('\n', '').replace('\r', '')
                result['address'] = text
        # video
        breadcrumb = soup.find('div', class_='breadcrumb')
        if breadcrumb:
            text = breadcrumb.get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        yield result

    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for one minute to close the spider')
        time.sleep(30)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')






























