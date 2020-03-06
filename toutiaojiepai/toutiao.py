import json
import multiprocessing
import random
import re

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urlencode
import time
import pymongo
from config import *
import os
from hashlib import md5
from json.decoder import JSONDecodeError

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

# headers = {
# :authority: www.toutiao.com
# :method: GET
# :path: /api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1583420572637
# :scheme: https
# accept: application/json, text/javascript
# accept-encoding: gzip, deflate, br
# accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
# content-type: application/x-www-form-urlencoded
# cookie: tt_webid=6800719909108237838; s_v_web_id=verify_k7et0a3m_n7W97Ezm_QTRE_4tI3_BuJq_VoUuJs7o5azv; WEATHER_CITY=%E5%8C%97%E4%BA%AC; SLARDAR_WEB_ID=vn; tt_webid=6800719909108237838; csrftoken=09398428d84744d49a245b365ec7a09a; __tasessionId=a2vf6i4tr1583419125696
# referer: https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D
# sec-fetch-mode: cors
# sec-fetch-site: same-origin
# user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36
# x-requested-with: XMLHttpRequest
# }
headers = {
    'authority': 'www.toutiao.com',
    'method': 'GET',
    'path': '/api/search/content/?aid=24&app_name=web_search&offset=100&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1556892118295',
    'scheme': 'https',
    'accept': 'application/json, text/javascript',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': 'tt_webid=6686738543769060877; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16a7d235d9041f-0e169f5e22e7b5-39395704-1fa400-16a7d235d9174e; tt_webid=6686738543769060877; csrftoken=dd5f783688e4d7cbdad02d2c327bdf7a; CNZZDATA1259612802=1082695115-1556872462-%7C1556883262; s_v_web_id=c24ad746965be967215f64165e913d08',
    'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def get_page_index(offset, keyword):
    timestamp = int(time.time())
    # timestamp = str(int(time.time()))
    print(timestamp)
    data = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': timestamp
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    # url = f'https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp={timestamp}'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        print('获取索引失败')
        return None
    except RequestException:
        print('异常')
        return None


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for items in data.get('data'):
                # 排除None值
                if items.get('article_url'):
                    yield items.get('article_url')
    except JSONDecoderError:
        pass


def get_page_detail(url):
    # headers_img = {
    #     'Referer': url,
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    # }
    try:
        # img = requests.get(url, headers=headers_img)
        # print(img.text)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错')
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    # print(soup)
    try:
        article_title = soup.select('title')[0].get_text()
        # article_content = soup.select('articleInfo')[0].get_text()
        print(article_title)
        # print(article_content)
    except IndexError:
        print('获取标题时的索引错误')
        article_title = '获取标题索引错误'

    # img_pattern = re.compile('<div class="pgc-img".*?<img src=(.*?) img_width', re.S)
    # print(html)
    img_pattern = re.compile('gallery: JSON.parse\\((.*?)\\)', re.S)
    # res = re.findall(img_pattern, html)
    res = re.search(img_pattern, html)
    if res:
        data_dic = eval(json.loads(res.group(1)))
        # print(data_dic)
        if data_dic and 'sub_images' in data_dic.keys():
            sub_images = data_dic.get('sub_images')
            images_url_lis = [item.get('url').replace('\\', '') for item in sub_images]
            # print(images_url_lis)
            for images_url_li in images_url_lis:
                save_image(download_image(images_url_li), article_title)
            return {
                'article_title': article_title,
                'url': url,
                'images_url_lis': images_url_lis
            }


def save_to_mongo(res_dic):
    if db[MONGO_TABALE].insert(res_dic):
        print('存储到MONGO成功', res_dic)
        return True
    return False


def download_image(url):
    print('当前正在下载： ', url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        return None
    except RequestException:
        return None


def save_image(content, title):
    path = f'{os.getcwd()}/{title}'
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path+f'/{md5(content).hexdigest()}.jpg', 'wb') as f:
        f.write(content)


def main(offset):
    random_time = random.randint(1, 3)
    print('随机等待时间: %ds'%random_time)
    time.sleep(random_time)
    html = get_page_index(offset, KEYWORDS)
    for url in parse_page_index(html):
        # print(url)
        html = get_page_detail(url)
        # print(html)
        if html:
            res_dic = parse_page_detail(html, url)
            if res_dic:
                save_to_mongo(res_dic)


if __name__ == '__main__':
    # 普通抓取
    for offset in range(0, 100, 20):
        main(offset)
    # # 多进程
    # pool = multiprocessing.Pool()
    # pool.map(main, [offset*20 for offset in range(GROUP_START, GROUP_END+1)])
