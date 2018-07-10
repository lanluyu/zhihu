# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class ZhihuspiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    '''
    son_href = Field()
    son_name = Field()
    son_content = Field()
    topic_name = Field()

    title = Field()
    name = Field()
    question_id = Field()
    topic = Field()
    '''
    question = Field()
    name = Field()    
    follower = Field()
    voteup_count = Field()
    comment_count = Field()
    content = Field()
    created_time = Field()

