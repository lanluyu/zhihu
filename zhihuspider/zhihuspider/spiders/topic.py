# -*- coding: utf-8 -*-
'''
这个 spider 单独统计知乎话题广场下的所有父话题及其子话题的个数
'''
from scrapy import Spider,Request,FormRequest
import json
from lxml import etree

class TopicSpider(Spider):
    name = 'topic'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    
    # 获取话题广场首页，解析并请求每个父话题的页面，获取其子话题
    def parse(self, response):
        topics = response.xpath('.//div[@class="zm-topic-cat-page"]/ul/li')
        for topic in topics:
            topic_name = topic.xpath('./a/text()').extract_first()
            topic_id = topic.xpath('./@data-id').extract_first()
            # print(topic_name,topic_id)

            # 父话题的 url
            topic_url = "https://www.zhihu.com/node/TopicsPlazzaListV2"
            # 请求父话题的页面，并交给parse_topic函数处理
            yield FormRequest(url=topic_url,callback=self.parse_topic,dont_filter=True,meta={"offset":0,"topic_id":topic_id,"name":topic_name},
                        formdata={"method": "next","params": json.dumps({"topic_id":topic_id,"offset":0,"hash_id":""})})

    def parse_topic(self,response):
        # 获取传递的变量
        offset = response.meta.get("offset")
        topic_id = response.meta.get("topic_id")
        topic_name = response.meta.get("name")
        # 解析获得的响应
        json_info = json.loads(response.text)  # 此时json_info为一个字典
        msg_info = json_info['msg']  # 键为 msg 的值对应为一个列表
        offset += len(msg_info)

        # 判断 msg_info 里的 msg 数量是否小于20，小于的话表示已经是最后一页，就不再请求了
        if not len(msg_info)<20: 
            yield FormRequest("https://www.zhihu.com/node/TopicsPlazzaListV2",callback=self.parse_topic,dont_filter=True,meta={"offset":offset,"topic_id":topic_id,"name":topic_name},
                    formdata={"method": "next","params": json.dumps({"topic_id":topic_id,"offset":offset,"hash_id":""})})
        else:
            print("name:{},topic_num:{}".format(topic_name,offset))



