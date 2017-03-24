# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from PCauto.items import PCautoMallGCTItem
import time
import re
from PCauto import pipelines


class PCautoMallGCTSpider(RedisSpider):
    name = 'PCauto_mall_gct'
    api_url = 'http://mall.pcauto.com.cn/gct/r%s/'
    mall_url = 'http://mall.pcauto.com.cn/'
    city_js_url = 'http://www.pcauto.com.cn/global/1603/intf8771.js'

    pipeline = set([pipelines.MallGCTPipeline, ])


    def start_requests(self):
        # yield Request(self.mall_url, callback=self.get_city)
        yield Request(self.city_js_url, callback=self.get_city)

    def get_city(self,response):
        body = response._body
        city_id_list = re.findall(r'"cityId":"(\d+)"',body)
        for city_id in city_id_list:
            yield Request(self.api_url % city_id, callback=self.get_tuangou)

        # soup = BeautifulSoup(response.body_as_unicode())
        # citys = soup.find('div', id='cityArea1').find_all('a')
        # for city in citys:
        #     city_id = city.get('data-mid')
        #     yield Request(self.api_url % city_id, callback=self.get_tuangou)

    def get_tuangou(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        btns = soup.find('div', class_='tuangoult02').find_all('div', class_='btn')
        for btn in btns:
            href = btn.find('a').get('href')
            yield Request(href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoMallGCTItem()

        result['category'] = '汽车商城-购车团'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for ten seconds to close the spider')
        time.sleep(10)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')
