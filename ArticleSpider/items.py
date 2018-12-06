# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join,TakeFirst

from ArticleSpider.utils.itemloadermanager import get_date, return_value, get_nums, remove_comment_tag


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()  # Field()能够接收和传递任何类型的值,类似于字典的形式
    create_date = scrapy.Field()  # 创建时间
    url = scrapy.Field()  # 文章路径
    front_img_url_download = scrapy.Field()
    fav_nums = scrapy.Field()  # 收藏数
    comment_nums = scrapy.Field()  # 评论数
    vote_nums = scrapy.Field()  # 点赞数
    tags = scrapy.Field()  # 标签分类 label
    content = scrapy.Field()  # 文章内容
    object_id = scrapy.Field()  # 文章内容的md5的哈希值，能够将长度不定的 url 转换成定长的序列
    front_img_path = scrapy.Field()  # 文件路径


class ArticleItemLoader(ItemLoader):
    """
    自定义 ItemLoader, 就相当于一个容器
    """
    # 这里表示，输出获取的 ArticleItemLoader 提取到的值，都是 list 中的第一个值
    # 如果有的默认不是取第一个值，就在 Field() 中进行修改
    default_output_processor = TakeFirst()


class JobBoleArticleLoaderItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(  # 创建时间
        input_processor=MapCompose(get_date),
        output_processor=Join("")
    )
    url = scrapy.Field()  # 文章路径
    front_img_url_download = scrapy.Field(  # 文章封面图片路径,用于下载，赋值时必须为数组形式
        # 默认 output_processor 是 TakeFirst()，这样返回的是一个字符串，不是 list，此处必须是 list
        # 修改 output_processor
        output_processor=MapCompose(return_value)
    )
    fav_nums = scrapy.Field(  # 收藏数
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(  # 评论数
        input_processor=MapCompose(get_nums)
    )
    vote_nums = scrapy.Field(  # 点赞数
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(  # 标签分类 label
        # 本身就是一个list, 输出时，将 list 以 commas 逗号连接
        input_processor=MapCompose(remove_comment_tag),
        output_processor=Join(",")
    )
    content = scrapy.Field(  # 文章内容
        # content 我们不是取最后一个，是全部都要，所以不用 TakeFirst()
        output_processor=Join("")
    )
    object_id = scrapy.Field()  # 文章内容的md5的哈希值，能够将长度不定的 url 转换成定长的序列
    front_img_path = scrapy.Field()  # 文件路径



