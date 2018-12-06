# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.spiders.CxExtractor import CxExtractor
from ArticleSpider.items import JobBoleArticleItem, JobBoleArticleLoaderItem, ArticleItemLoader
from ArticleSpider.utils.common import gen_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'

    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 获取下一页的url，交给下一页下载
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first()
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": parse.urljoin(response.url, image_url)}, callback=self.parse_loaderdetail)

        # 提取下一页下载
        """
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)
        """

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        # 通过CSS选择器
        # title_css = response.css(".entry-header h1::text").extract()[0]
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip() \
            .replace("·", "").strip()
        # //*[@id="post-114377"]/div[2]/p
        category = response.xpath("//p[@class='entry-meta-hide-on-mobile']").extract()[0]
        # tag = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a")
        # tags1 = tag.xpath("string(.)").extract()
        # 点赞
        # praise_nums = response.xpath("//span[contains(@class,'vote-post-up)]").extract()[0]
        votes_css = response.css(".vote-post-up h10::text").extract_first()
        if votes_css:
            vote_nums = int(votes_css)
        else:
            vote_nums = 0
        # 收藏
        ma_fav_css = re.match(".*?(\d+).*", response.css(".bookmark-btn::text").extract_first())
        if ma_fav_css:
            fav_nums = int(ma_fav_css.group(1))
        else:
            fav_nums = 0
        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        # content = response.xpath("//div[@class='entry']").extract()[0]
        tags = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tags = [element for element in tags if not element.strip().endswith("评论")]
        tag = ','.join(tags)
        front_img_url_download = response.meta.get("front_image_url", "")
        # print(front_image_url)
        # 提取文章的具体字段
        cx = CxExtractor(threshold=186)
        html_content = cx.filter_tags(response.text)
        s_content = cx.getText(html_content)
        article_item["title"] = title
        article_item["create_date"] = create_date
        article_item["url"] = response.url
        article_item["front_img_url_download"] = [front_img_url_download]  # 这里传递的需要是列表的形式，否则后面保存图片的时候，会出现类型错误，必须是可迭代对象
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["vote_nums"] = vote_nums
        article_item["tags"] = tag
        # article_item["cpyrights"] = cpyrights
        article_item["content"] = s_content  # 存入数据库的时候，需要转换成字符串
        article_item["object_id"] = gen_md5(response.url)
        yield article_item

    def parse_loaderdetail(self, response):
        front_img_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticleLoaderItem(), response=response)
        article_item_loader = JobBoleArticleLoaderItem()
        item_loader.add_css("title", ".entry-header h1::text")  # 通过 css 选择器获取值
        item_loader.add_value("url", response.url)
        item_loader.add_css("create_date", ".entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_img_url_download", [front_img_url])
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("vote_nums", ".vote-post-up h10::text")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")
        #item_loader.add_css("content", ".entry *::text")
        item_loader.add_value("object_id", gen_md5(response.url))
        # item_loader.add_xpath()
        # item_loader.add_value()
        cx = CxExtractor(threshold=186)
        html_content = cx.filter_tags(response.text)
        s_content = cx.getText(html_content)
        item_loader.add_value("content",s_content)
        article_item_loader = item_loader.load_item()
        yield article_item_loader
