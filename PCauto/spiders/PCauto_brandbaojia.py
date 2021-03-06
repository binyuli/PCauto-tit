# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import json
from PCauto.mongodb import mongoservice
from PCauto.items import PCautoBrandbaojiaUrlItem
from PCauto import pipelines

class PCautoBrandBaojiaSpider(RedisSpider):
    name = 'PCauto_baojia'
    pipeline = set([pipelines.BrandBaojiaPipeline, ])

    def start_requests(self):
        baojia_urls = mongoservice.get_baojia_url()
        for url in baojia_urls :
            yield Request(url, dont_filter=True, callback=self.get_vehicleTypes)
            yield Request(url, callback=self.get_url)

    def get_vehicleTypes(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        # 有可能没有 typeList
        typeList = soup.find('div',id="typeList")
        if typeList:
            vehicles = typeList.find_all('li')
            for vehicle in vehicles:
                href = vehicle.find('a').get('href')
                yield Request(href, callback=self.save_vehicleType)

    def save_vehicleType(self,response):
        # start save vehicleType index
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')

        result = dict()
        result['category'] = '车型首页'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        position = soup.find('div', class_="position")
        # 平行进口车没有 position
        if position:
            text = position.find('div', class_="pos-mark").get_text().strip().replace('\n', '').replace('\r','')
            result['address'] = text

        put_result = json.dumps(dict(result), ensure_ascii=False, sort_keys=True, encoding='utf8').encode('utf8')
        save_result = json.loads(put_result)
        mongoservice.save_vehicleType(save_result)

        # request for vehicleType_baojia
        yield Request(response.url + 'price.html', callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandbaojiaUrlItem()
        result['category'] = '报价'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
        position = soup.find('div',class_="position")
        if position:
            # 车系 position (class = 'position')
            place = position.find('div',class_="pos-mark")
            if place:
                text = place.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
            # 车型 position (class = 'wrap position')
            mark = position.find('span',class_="mark")
            if mark:
                text = mark.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
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