# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
import math
from PCauto.items import PCautoDealerModelItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerModelSpider(RedisSpider):
    name = 'PCauto_dealer_model'
    pipeline = set([pipelines.DealerModelPipeline, ])
    root_url = 'http://price.pcauto.com.cn'

    def start_requests(self):
        urls = mongoservice.get_dealer_model()
        for url in urls:
            yield Request(url, dont_filter=True, callback=self.get_page)
            yield Request(url, callback=self.get_url)

    def get_page(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        model = soup.find('div', id='model').find('i').find('em').get_text()
        if model:
            # make page root url
            ma = re.search(r'(.*)/model', response.url)
            suffix = '/p%d/model.html#model'
            page_url = ma.group(1) + suffix

            # catch page amount
            ma = re.search(r'\d+', model)
            model_amount = ma.group()

            model_num = math.ceil(float(model_amount)/8)
            for page_num in range(1,int(model_num) + 1):
                yield Request(page_url % page_num, dont_filter=True, callback=self.get_car)
                yield Request(page_url % page_num, callback=self.get_url)

    def get_car(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        car_list = soup.find('dl', class_="tjlist allchex clearfix").find_all('div',class_='autobox')
        for car in car_list:
            href = car.find('span').find('a').get('href')
            yield Request(href, dont_filter=True, callback=self.get_vehicleModel)
            yield Request(href, callback=self.get_url)


    def get_vehicleModel(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        vehicle_list = soup.find_all('dl', class_='chextab clearfix')
        for list in vehicle_list:
            vehicles = list.find_all('dd')
            for vehicle in vehicles:
                href = vehicle.find('div', class_='div01').find('a').get('href')
                yield Request(self.root_url + href, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerModelItem()
        result['category'] = '经销商-车型展厅'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for half minute to close the spider')
        time.sleep(30)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')