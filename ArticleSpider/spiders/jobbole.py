# -*- coding: utf-8 -*-
import scrapy
import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/114377/']

    def parse(self, response):
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·", "").strip()
        #//*[@id="post-114377"]/div[2]/p
        category = response.xpath("//p[@class='entry-meta-hide-on-mobile']").extract()[0]
        tag = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a")
        tags1 = tag.xpath("string(.)").extract()
        #点赞
        praise_nums=response.xpath("//span[contains(@class,'vote-post-up)]").extract()[0]
        #收藏
        fav_nums=response.xpath("//span[contains(@class,'bookmark-btn)]").extract()[0]
        match_re = re.match(".*(\d+).*",fav_nums)
        if match_re:
            fav_nums=match_re.group(1)
        #评论
        comment_nums=response.xpath("//a[@href='#article-comment'/span").extract()[0]
        match_re = re.match(".*(\d+).*",comment_nums)
        if match_re:
            comment_nums=match_re.group(1)
        print(tags1)
        print(create_date)
        pass
