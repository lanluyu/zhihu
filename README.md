zhihu说明文档
==
介绍
 - 
zhihu是一个知乎话题内容的爬虫，可以爬取知乎所有的话题相关的问答内容，爬虫框架使用scrapy，数据存储使用mongo。由于知乎话题的问答内容信息巨大（亿级数据量），这里只是爬取了话题广场的“阅读”话题下的所有子话题下的精华问题与回答的相关信息。<br>

代码说明
--
### 运行环境
* Windows 10 专业版<br>
* Python 3.5/Scrapy 1.5.0/MongoDB 3.4.7<br>

### 依赖包
* Requests<br>
* Pymongo<br>
* Faker(随机切换User-Agent)<br>

### 其它
知乎话题广场有33个父话题，每个父话题有不同数量的子话题，每个子话题下又有很多的精华问题，每个精华问题下有不同数量的回答，如果想要完全爬取所有的问答，由于数据量太大，耗时太久。这里选择了“阅读”话题进行数据爬取。知乎的子话题、精华问答的内容都是采用动态加载的方法进行更新获取的，在分析了其动态加载链接后，从当前页面获取链接所需的参数并构造正确的链接，进行了三级深入的爬取。爬取过程中设置下载延迟为1S，知乎没有对这种低频率的访问做限制。

## 流程图

![流程图](https://github.com/lanluyu/zhihu/blob/master/pic/%E6%B5%81%E7%A8%8B%E5%9B%BE.PNG)

* 请求(https://www.zhihu.com/topics) 获取页面中所有的父话题及其id,父话题的链接需要POST请求，需要其id。
![父话题](https://github.com/lanluyu/zhihu/blob/master/pic/topic.PNG)

* 请求到的父话题页面，然后获取所有子话题，如下图：
![子话题](https://github.com/lanluyu/zhihu/blob/master/pic/topics.PNG)

* 进入到单个子话题页面，点击“精华”，获取精华问题，如下图：
![精华问题](https://github.com/lanluyu/zhihu/blob/master/pic/question.PNG)

* 进入到单个精华问题页面，获取其全部的回答。
![精华问题回答](https://github.com/lanluyu/zhihu/blob/master/pic/anwser.PNG)

* 在精华问题的全部回答页面，能够获取全部的回答数、答题者id、粉丝数、答题内容、点赞数和相关的评论数，如下图：
![read](https://github.com/lanluyu/zhihu/blob/master/pic/bufen.PNG)


爬取结果
-
* 整个爬取过程持续了80个小时，总共获取了1140727条数据，结果存储在MongoDB中。再导出为Excle文件。部分数据如下截图:<br>
![部分问答信息](https://github.com/lanluyu/zhihu/blob/master/pic/mongodb.PNG)
* 根据2974个问题制作的词云如下：<br>
![词云](https://github.com/lanluyu/zhihu/blob/master/pic/lanluyu%E8%AF%8D%E4%BA%91%E5%9B%BE20180711.png)


