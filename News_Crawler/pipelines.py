# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from News_Crawler import utils
import os, math, re


class SaveChunkFilePipeline(object):

    def __init__(self):
        self.file_chunk_size = utils.get_file_chunk_size()
        self.save_dir = "../Data/{}".format(utils.get_time_str())
        utils.mkdirs(self.save_dir)
        self.data = {}

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
        items.append(item)

        return item

    def close_spider(self, spider):
        # Save all items scrapped by spider
        spider_name = spider.name
        map_category_items = self.data.get(spider_name)
        # spider_save_dir = os.path.join(self.save_dir, spider_name)
        file_chunk_size = self.file_chunk_size
        for category, items in map_category_items.items():
            category_save_dir = os.path.join(self.save_dir, spider_name, category)
            num_files = int(math.ceil(len(items) / file_chunk_size))
            for file_idx in range(0, num_files):
                # Save one file
                save_path = os.path.join(category_save_dir, "{}_{}.json".format(category, file_idx+1))
                start_idx = file_idx * file_chunk_size
                end_idx = start_idx + file_chunk_size
                utils.save_json(items[start_idx: end_idx], save_path)
                spider.log("Save {} items to {} done".format(len(items), save_path))


class CleanItemPipeline(object):

    def __init__(self):
        self.re = re.compile("[^\w\s]")

    def process_item(self, item, spider):

        item["title"] = self.re.sub('', item["title"].strip())
        item["category"] = self.re.sub('', item["category"].strip())

        return item
