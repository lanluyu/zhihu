# -*- coding: utf-8 -*-
'''
这个 spider 获取游戏话题下子栏目的所有的精华的问题题目
'''
from scrapy import Spider,Request,FormRequest
import json
from lxml import etree
from zhihuspider.items import ZhihuspiderItem

class QuestionSpider(Spider):
    name = 'question'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    topic_question = 'https://www.zhihu.com/api/v4/topics/{}/feeds/essence?limit={}&offset={}'
    
    # 获取话题广场首页，解析并请求每个父话题的页面，获取其子话题
    def parse(self, response):
        topics = response.xpath('.//div[@class="zm-topic-cat-page"]/ul/li')
        '''
        for topic in topics:
            topic_name = topic.xpath('./a/text()').extract_first()
            topic_id = topic.xpath('./@data-id').extract_first()
            # print(topic_name,topic_id)
        '''

        # 父话题的 url
        topic_url = "https://www.zhihu.com/node/TopicsPlazzaListV2"
        # 请求父话题的页面，并交给parse_topic函数处理
        yield FormRequest(url=topic_url,callback=self.parse_topic,dont_filter=True,meta={"offset":0,"topic_id":253,"name":'游戏'},
                    formdata={"method": "next","params": json.dumps({"topic_id":253,"offset":0,"hash_id":""})})

    def parse_topic(self,response):
        # 获取传递的变量值
        offset = response.meta.get("offset")
        topic_id = response.meta.get("topic_id")
        topic_name = response.meta.get("name")
        # 解析父话题“游戏”页面
        json_info = json.loads(response.text)  # 此时json_info为一个字典
        msg_info = json_info['msg']            # 键为 msg 的值对应为一个列表
        offset += len(msg_info)
        # 获取子话题的“精华问题”页面所需的参数，构造好url后再给parse_topic解析
        for msg in msg_info:
            html = etree.HTML(msg)
            href = html.xpath('.//a[@target="_blank"]/@href')
            num = href[0].split('/')[-1]
            yield Request(self.topic_question.format(num,10,0),callback=self.parse_question,dont_filter=True,
                            meta={"offset":0,"limit":10,"num":num,'name':topic_name})
        # 获取父话题“阅读”下的所有子话题
        if not len(msg_info['msg'])<20:
            yield FormRequest("https://www.zhihu.com/node/TopicsPlazzaListV2",callback=self.parse_topic,dont_filter=True,meta={"offset":offset,"topic_id":253,"name":'游戏'},
                    formdata={"method": "next","params": json.dumps({"topic_id":253,"offset":offset,"hash_id":""})})
        else:
            print("name:{},topic_num:{}".format(name,offset))
 
    def parse_question(self,response):
        offset = response.meta.get('offset')
        limit = response.meta.get('limit')
        num = response.meta.get('num')
        name = response.meta.get("name")
        # 解析“精华问题”页面。
        json_info = json.loads(response.text)
        data_info = json_info['data']
        offset += len(data_info)
        # 获取“精华问题”的相关信息
        for data in data_info:
            item = ZhihuspiderItem()
            if 'zhuanlan' in data['target']['url']:
                continue
            item['title'] = data['target']['question']['title']
            item['name'] = data['target']['author']['name']
            item['question_id'] = data['target']['question']['id']
            item['topic'] = name
            print(item)
            yield item
        # 如果一页获取的问题数大于等于10，就说明还没有获取完，需要继续获取
        if not len(data_info) < 10:
            yield Request(self.topic_question.format(num,10,offset),callback=self.parse_question,dont_filter=True,
                                meta={"offset":0,"limit":10,"num":num})
        else:
            print("num:{},offset:{}".format(num,offset))
        