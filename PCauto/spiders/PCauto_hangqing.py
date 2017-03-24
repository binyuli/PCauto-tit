# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto import pipelines
from PCauto.items import PCautoHangqingItem

class PCautoHangqingSpider(RedisSpider):
    name = 'PCauto_hangqing'
    nav_urls = ['http://www.pcauto.com.cn/qcbj/quanguo/ddyd/','http://www.pcauto.com.cn/qcbj/quanguo/csdp/']

    pipeline = set([pipelines.HangqingPipeline, ])

    def start_requests(self):
        for url in self.nav_urls:
            yield Request(url, dont_filter=True, callback=self.get_page)
            yield Request(url, callback=self.get_url)

    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(),'lxml')
        articles = soup.find('div', class_='box list').find_all('div', class_='pic-txt clearfix')
        for article in articles:
            href = article.find('div', class_='txt').find('p', class_='tit blue').find('a').get('href')
            yield Request(href, callback=self.get_url)

        page_info = soup.find('div', class_='pcauto_page')
        if page_info:
            next_page = page_info.find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoHangqingItem()

        result['category'] = '行情'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="guide")
        if place:
            mark = place.find('span',class_="mark")
            if mark:
                text = mark.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
            crumbs = place.find('div', class_='crumbs')
            if crumbs:
                text = crumbs.get_text().strip().replace('\n', '').replace('\r', '')
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





























