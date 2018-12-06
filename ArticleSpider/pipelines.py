# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import codecs

from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def __init__(self):
        # 连接数据库
        self.conn = MySQLdb.connect('localhost', 'spider', 'wuzhenyu', 'article_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
                    insert into bole_article(title, create_date, url, url_object_id, front_img_url, front_img_path, comment_nums, 
                    fav_nums, vote_nums, tags, content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, %d, '%s', '%s')
                """ % (item["title"], item["create_date"], item["url"], item["object_id"], item["front_img_url"],
                       item["front_img_path"], item["comment_nums"], item["fav_nums"], item["vote_nums"], item["tags"],
                       item["content"])

        self.cursor.execute(insert_sql)
        self.conn.commit()

    def spider_close(self, spider):
        self.cursor.close()
        self.conn.close()


class MysqlTwistedPipeline(object):
    """
    利用 Twisted API 实现异步入库 MySQL 的功能
    Twisted 提供的是一个异步的容器，MySQL 的操作还是使用的MySQLDB 的库
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """
        被 spider 调用，将 settings.py 传递进来，读取我们配置的参数
        模仿 images.py 源代码中的 from_settings 函数的写法
        """
        # 字典中的参数，要与 MySQLdb 中的connect 的参数相同
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )

        # twisted 中的 adbapi 能够将sql操作转变成异步操作
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用 twisted 将 mysql 操作编程异步执行
        """
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # handle exceptions

    def handle_error(self, failure):
        """
        处理异步操作的异常
        """
        print(failure)

    def do_insert(self, cursor, item):
        """
        执行具体的操作，能够自动 commit
        """
        image_download = json.dumps(item["front_img_url_download"])
        print(image_download)
        insert_sql = """
                    insert into bole_article(title, create_date, url, url_object_id, front_img_url, front_img_path, comment_nums, 
                    fav_nums, vote_nums, tags, content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s','%s', '%s','%s', '%s', '%s');
                """ % (item["title"], item["create_date"], item["url"], item["object_id"], image_download,
                       item["front_img_path"], item["comment_nums"], item["fav_nums"], item["vote_nums"], item["tags"],
                       item["content"])

        #cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["object_id"], image_download,
        #               item["front_img_path"], item["comment_nums"], item["fav_nums"], item["vote_nums"], item["tags"],
         #              item["content"]))
        print(insert_sql)
        cursor.execute(insert_sql)


class JsonExporterPipeline(object):
    # 调用scrapy提供的json_export导出json文件
    def __init__(self):
        self.file = open("articleexport.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class JsonWithEncodeingpeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            if not ok:
                image_file_path = ''
            else:
                image_file_path = value["path"]
        item["front_img_path"] = image_file_path
        return item
