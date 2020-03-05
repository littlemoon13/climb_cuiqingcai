import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode
import time


def get_page_index(offset, keyword):
    timestamp = int(time.time())
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
    # url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    # url = f'https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp={timestamp}'
    url = 'http://desk.zol.com.cn/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        print('获取索引失败')
        return None
    except RequestException:
        print('异常')
        return None


def main():
    html = get_page_index(0, '街拍')
    print(html)


if __name__ == '__main__':
    main()
