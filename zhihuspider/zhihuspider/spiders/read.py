# -*- coding: utf-8 -*-
'''
这个 spider 单独请求知乎话题广场下的“阅读”父话题下的59个子话题，
并请求59个子话题下的“精华问题”目录下的所以问题及其答案
'''
from scrapy import Spider,Request,FormRequest
import json
from lxml import etree
from zhihuspider.items import ZhihuspiderItem

class ReadSpider(Spider):
    name = 'read'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    topic_question = 'https://www.zhihu.com/api/v4/topics/{}/feeds/essence?limit={}&offset={}'
    topic_anwser = ('https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment'
                   +'%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky'
                   +'%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count'
                   +'%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info'
                   +'%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata'
                   +'%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer'
                   +'%29%5D.topics&limit={}&offset={}')   # 去掉某些参数后数据缺失，所以无法简化此 url

    # 获取话题广场首页，解析并请求每个父话题的页面，获取其子话题
    def parse(self, response):
        topics = response.xpath('.//div[@class="zm-topic-cat-page"]/ul/li')
        '''
        for topic in topics:
            name = topic.xpath('./a/text()').extract_first()
            topic_id = topic.xpath('./@data-id').extract_first()
            # print(topic_name,topic_id)
        '''
        # 父话题的 url
        topic_url = "https://www.zhihu.com/node/TopicsPlazzaListV2"
        # 请求父话题的页面，并交给parse_topic函数处理，因为只请求“阅读”话题，所以 "topic_id":113。实际上此函数可另写
        yield FormRequest(url=topic_url,callback=self.parse_topic,dont_filter=True,meta={"offset":0,"topic_id":113,"name":'阅读'},
                    formdata={"method": "next","params": json.dumps({"topic_id":113,"offset":0,"hash_id":""})})

    def parse_topic(self,response):
        # 获取传递的变量值
        offset = response.meta.get("offset")
        topic_id = response.meta.get("topic_id")
        name = response.meta.get("name")
        # 解析父话题“阅读”页面
        json_info = json.loads(response.text)  # 此时json_info为一个字典
        msg_info = json_info['msg']  # 键为 msg 的值对应为一个列表
        offset += len(msg_info)
        # 获取子话题的“精华问题”页面所需的参数，构造好url后再给parse_topic解析
        for msg in msg_info:
            html = etree.HTML(msg)
            href = html.xpath('.//a[@target="_blank"]/@href')
            num = href[0].split('/')[-1]
            topic_name = html.xpath('.//strong/text()')
            yield Request(self.topic_question.format(num,10,0),callback=self.parse_question,dont_filter=True,
                            meta={"offset":0,"limit":10,"num":num,'name':name,'topic_name':topic_name[0]})
        # 获取父话题“阅读”下的所有子话题
        if not len(msg_info['msg'])<20:
            yield FormRequest("https://www.zhihu.com/node/TopicsPlazzaListV2",callback=self.parse_topic,dont_filter=True,meta={"offset":offset,"topic_id":113,"name":'阅读'},
                    formdata={"method": "next","params": json.dumps({"topic_id":113,"offset":offset,"hash_id":""})})
        else:
            print("name:{},topic_num:{}".format(name,offset))

    def parse_question(self,response):
        offset = response.meta.get('offset')
        limit = response.meta.get('limit')
        num = response.meta.get('num')
        name = response.meta.get("name")
        topic_name = response.meta.get("topic_name")
        # 解析“精华问题”页面，
        json_info = json.loads(response.text)
        data_info = json_info['data']
        offset += len(data_info)
        # 获取“问题”的页面链接所需的参数，构造页面链接，交给parse_anwser函数处理，获取该问题的所有答案信息
        for data in data_info:
            if 'zhuanlan' in data['target']['url']:
                continue
            anwser_id = data['target']['question']['id']            
            yield Request(self.topic_anwser.format(anwser_id,5,0),callback=self.parse_anwser,dont_filter=True,
                                meta={"offset":0,"limit":5,"anwser_id":anwser_id})
        # 如果一页获取的问题数大于等于10，就说明还没有获取完，需要继续获取
        if not len(data_info) < 10:
            yield Request(self.topic_question.format(num,limit,offset),callback=self.parse_question,dont_filter=True,
                                meta={"offset":offset,"limit":limit,"num":num})
        else:
            print("num:{},offset:{}".format(num,offset))

    def parse_anwser(self,response):
        name = response.meta.get('name')
        topic_name = response.meta.get('topic_name')
        offset = response.meta.get('offset')
        limit = response.meta.get('limit')
        anwser_id = response.meta.get('anwser_id')
        # 解析获得的单个精华问题的答案页面
        json_info = json.loads(response.text)
        data_info = json_info['data']
        offset = offset+len(data_info)
        # 解析含有答案内容的 json 内容
        for data in data_info:
            item = ZhihuspiderItem()
            item['question'] = data['question']['title']            # 问题题目
            item['name'] = data['author']['name']                   # 答题人id
            item['follower'] = data['author']['follower_count']     # 答题人粉丝数
            item['voteup_count'] = data['voteup_count']             # 赞了该答案的人数
            item['comment_count'] = data['comment_count']           # 评论数
            item['content'] = data['content']                       # 答案内容
            item['created_time'] = data['created_time']             # 创建时间

            # print(item)            
            yield item 
        # 如果获取的答案数小于总的答案数，就继续获取
        paging_info = json_info['paging']
        if offset < paging_info['totals']:
            yield Request(self.topic_anwser.format(anwser_id,limit,offset),callback=self.parse_anwser,dont_filter=True,
                                meta={"offset":offset,"limit":limit,"anwser_id":anwser_id})
        else:            
            print("anwser_id:{},offset:{}".format(anwser_id,offset))
