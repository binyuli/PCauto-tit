# -*- coding: utf-8 -*-

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.log import configure_logging

from spiders.PCauto_start_urls import PCautoBrandListUrlSpider
from spiders.PCauto_brandinfo import PCautoBrandinfoSpider
from spiders.PCauto_brandconfig import PCautoBrandConfigSpider
from spiders.PCauto_brandbaojia import PCautoBrandBaojiaSpider
from spiders.PCauto_usedcar import PCautoUsedcarSpider
from spiders.PCauto_brandArticle import PCautoArticleSpider
from spiders.PCauto_picture import PCautoBrandPictureSpider
from spiders.PCauto_comment import PCautoCommentSpider
from spiders.PCauto_owner_price import PCautoOwnerPriceSpider
from spiders.PCauto_brand_baoyang import PCautoBaoyangSpider
from spiders.PCauto_dealer import PCautoDealerSpider
from spiders.PCauto_brand_youhui import PCautoBrandYouhuiSpider
from spiders.PCauto_forum import PCautoForumSpider
from spiders.PCauto_forum_city import PCautoCityForumSpider
from spiders.PCauto_forum_theme import PCautoThemeForumSpider
from spiders.PCauto_dealer_contact import PCautoDealerContactSpider
from spiders.PCauto_dealer_model import PCautoDealerModelSpider
from spiders.PCauto_dealer_market import PCautoDealerMarketSpider
from spiders.PCauto_dealer_news import PCautoDealerNewsSpider

import pymongo

# the spider we need to scheduler
BaojiaUrlSpider = PCautoBrandBaojiaSpider()
ConfigSpider = PCautoBrandConfigSpider()
BrandInfoSpider = PCautoBrandinfoSpider()
PCautoStartSpider = PCautoBrandListUrlSpider()
UsedCarUrlSpider = PCautoUsedcarSpider()
ArticleSpider = PCautoArticleSpider()
PictureSpider = PCautoBrandPictureSpider()
CommentSpider = PCautoCommentSpider()
OwnerPriceSpider = PCautoOwnerPriceSpider()
BaoyangSpider = PCautoBaoyangSpider()
DealerSpider = PCautoDealerSpider()
DealerContactSpider = PCautoDealerContactSpider()
DealerModelSpider = PCautoDealerModelSpider()
DealerMarketSpider = PCautoDealerMarketSpider()
DealerNewsSpider = PCautoDealerNewsSpider()
BrandYouhuiSpider = PCautoBrandYouhuiSpider()
ForumSpider = PCautoForumSpider()
ForumCitySpider = PCautoCityForumSpider()
ForumThemeSpider = PCautoThemeForumSpider()


connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
db = connection[settings['MONGODB_DB']]

configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    # yield runner.crawl(PCautoStartSpider)
    # yield runner.crawl(BrandInfoSpider)
    # yield runner.crawl(ConfigSpider)
    # yield runner.crawl(BaojiaUrlSpider)
    yield runner.crawl(UsedCarUrlSpider)
    # yield runner.crawl(ArticleSpider)
    # yield runner.crawl(PictureSpider)
    # yield runner.crawl(CommentSpider)
    # yield runner.crawl(OwnerPriceSpider)
    # yield runner.crawl(BaoyangSpider)
    # yield runner.crawl(BrandYouhuiSpider)
    # yield runner.crawl(DealerSpider)
    # yield runner.crawl(DealerContactSpider)
    # yield runner.crawl(DealerModelSpider)
    # yield runner.crawl(DealerMarketSpider)
    # yield runner.crawl(DealerNewsSpider)
    # yield runner.crawl(ForumCitySpider)
    # yield runner.crawl(ForumThemeSpider)
    # yield runner.crawl(ForumSpider)
    reactor.stop()


crawl()
reactor.run()  # the script will block here until the last crawl call is finished