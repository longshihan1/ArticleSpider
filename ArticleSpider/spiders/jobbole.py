# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.spiders.CxExtractor import CxExtractor
from ArticleSpider.items import JobBoleArticleItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'

    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        #获取下一页的url，交给下一页下载
        post_nodes=response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url=post_node.css("img::attr(src)").extract_first("")
            post_url=post_node.css("::attr(href)").extract_first()
            yield Request(url=parse.urljoin(response.url,post_url), meta={"front_image_url": parse.urljoin(response.url, image_url)}, callback=self.parse_detail)

        #提取下一页下载
        next_urls=response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)
    def parse_detail(self, response):
        article_item=JobBoleArticleItem()
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        #通过CSS选择器
        title_css = response.css(".entry-header h1::text").extract()[0]
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip()\
            .replace("·", "").strip()
        #//*[@id="post-114377"]/div[2]/p
        category = response.xpath("//p[@class='entry-meta-hide-on-mobile']").extract()[0]
        #tag = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a")
        #tags1 = tag.xpath("string(.)").extract()
        # 点赞
        praise_nums = response.xpath("//span[contains(@class,'vote-post-up)]").extract()[0]
        # 收藏
        fav_nums = response.xpath("//span[contains(@class,'bookmark-btn)]").extract()[0]
        match_re = re.match(".*(\d+).*", fav_nums)
        if match_re:
            fav_nums = match_re.group(1)

        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums=int(match_re.group(1))
        else:
            comment_nums=0
        #content = response.xpath("//div[@class='entry']").extract()[0]
        tags=response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tags=[element for element in tags if not element.strip().endswith("评论")]
        print(tags)
        front_image_url=response.meta.get("front_image_url", "")
        print(front_image_url)
        # 提取文章的具体字段
        cx = CxExtractor(threshold=186)
        html_content = cx.filter_tags(response.text)
        s_content = cx.getText(html_content)
        print(s_content)
        pass