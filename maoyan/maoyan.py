import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
import re

def get_onepage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


def parse_one_page(html):
    # pattern = re.compile('.*?<main id="body">.*?<li class="media thread tap.*?')
    # pattern = re.compile('<main id="body">.*?<a href="thread.*?">(.*?)</a></main>', re.S)
    pattern = re.compile('<li class="media thread tap.*?<a href="thread.*?">(.*?)</a>'
                         + '.*?<span class="username text.*?">(.*?)</span>'
                         + '.*?<span class="date text-grey.*?">(.*?)</span>'
                         , re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {'content': item[0],
               'usename': item[1],
               'date': item[2]
               }


def write_to_file(content):
    with open('out_climb.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(idx):
    # url = 'http://cn.python-requests.org/zh_CN/latest/'
    # url = 'https://sci-hub.tw/'
    # url = 'http://cajn.cnki.net/gzbd/brief/Default.aspx'
    # url = 'https://music.163.com/#/discover/toplist?id=2250011882'
    # url = 'http://hao123.zongheng.com/'
    # url = 'http://j2.ac.cn/'
    url = f'http://j2.ac.cn/index-{idx}.htm'
    html = get_onepage(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    # 普通爬取方法
    # for idx in range(1, 4):
    #     main(idx)

    # 加入进程池
    pool = Pool()
    pool.map(main, [idx for idx in range(1, 4)])