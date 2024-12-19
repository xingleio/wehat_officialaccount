import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs
import time

class WechatCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_biz(self, url):
        """从URL中提取biz参数"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            return query.get('__biz', [None])[0]
        except:
            return None

    def get_history_articles(self, url, cookie):
        """获取历史文章列表"""
        biz = self.extract_biz(url)
        if not biz:
            raise Exception("无法获取公众号ID")

        # 更新headers中的cookie
        self.headers['Cookie'] = cookie
        articles = []
        offset = 0
        
        try:
            # 历史文章API地址
            api_url = f"https://mp.weixin.qq.com/mp/profile_ext"
            params = {
                '__biz': biz,
                'action': 'getmsg',
                'offset': offset,
                'count': 10,
                'f': 'json'
            }
            
            response = requests.get(api_url, headers=self.headers, params=params)
            data = response.json()
            
            if data.get('ret') != 0:
                raise Exception("获取文章列表失败，请检查Cookie是否有效")
            
            # 解析文章列表
            msg_list = json.loads(data['general_msg_list'])['list']
            
            for msg in msg_list:
                if 'app_msg_ext_info' in msg:
                    info = msg['app_msg_ext_info']
                    article = {
                        'title': info['title'],
                        'url': info['content_url'],
                        'digest': info['digest'],
                        'create_time': msg.get('comm_msg_info', {}).get('datetime', ''),
                        'cover': info.get('cover')
                    }
                    articles.append(article)
                    
                    # 处理多图文消息
                    if info.get('is_multi') == 1 and info.get('multi_app_msg_item_list'):
                        for sub_msg in info['multi_app_msg_item_list']:
                            sub_article = {
                                'title': sub_msg['title'],
                                'url': sub_msg['content_url'],
                                'digest': sub_msg['digest'],
                                'create_time': msg.get('comm_msg_info', {}).get('datetime', ''),
                                'cover': sub_msg.get('cover')
                            }
                            articles.append(sub_article)
            
            return articles
                
        except Exception as e:
            raise Exception(f"获取历史文章失败: {str(e)}")