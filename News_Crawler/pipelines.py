# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from News_Crawler import utils
import os, math, re


class SaveFilePipeline(object):

    def __init__(self):
        # self.file_chunk_size = utils.get_file_chunk_size()
        self.time_now_str = utils.get_time_str()
        self.base_dir = "./Data/Archive"
        self.data = {}
        self.export_format = utils.get_export_format_setting()
        self.export_fields = utils.get_export_fields_setting()

    def open_spider(self, spider):
        self.data.update({spider.name: {}})

    def process_item(self, item, spider):
        # Append data to collection to finally save to chunk files
        category = item.get("category")
        map_category_items = self.data.get(spider.name)
        items = map_category_items.get(category)
        if items is None:
            items = []
            map_category_items.update({category: items})
        items.append(dict(item))

        return item

    def close_spider(self, spider):
        # Save all items scrapped by spider
        spider_name = spider.name
        map_category_items = self.data.get(spider_name)
        # spider_save_dir = os.path.join(self.save_dir, spider_name)
        for category, items in map_category_items.items():
            category_save_dir = os.path.join(self.base_dir, spider_name, category)
            utils.mkdirs(category_save_dir)
            save_path = os.path.join(category_save_dir, "{}_{}_{}_{}articles.{}".format(
                spider_name, category, self.time_now_str, len(items), self.export_format))
            # Save items with format setting
            self.save_data(items, save_path, spider.logger)

    def save_data(self, items, save_path, logger):
        if self.export_format == "json":
            utils.save_json(items, save_path)
        else:
            utils.save_csv(items, save_path, fields=self.export_fields)
            
        logger.info("Save {} items to {} done".format(len(items), save_path))


class CleanItemPipeline(object):

    def __init__(self):
        self.re = re.compile(r"[^\w\s]")

    def process_item(self, item, spider):

        # Convert None to empty str
        item["url"] = item["url"] or ''
        item["title"] = item["title"] or ''
        item["time"] = item["time"] or ''
        item["intro"] = item["intro"] or ''
        item["content"] = item["content"] or ''
        item["category"] = item["category"] or ''
        item["lang"] = item["lang"] or ''

        # Replace special character
        item["title"] = self.re.sub('', item["title"].strip())
        item["category"] = self.re.sub('', item["category"].strip())

        item["intro"] = re.sub("\s+", ' ', item["intro"]).strip()
        item["content"] = re.sub("\s+", ' ', item["content"]).strip()

        return item


class TransformItemPipeLine(object):

    def process_item(self, item, spider):
        # time_str = '_'.join(item["time"].split(", ")[1:])
        # item["time"] = time_str

        return item
