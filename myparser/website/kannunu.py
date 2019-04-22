import urllib.request

import pyquery.pyquery as pq

from myparser.parser_template import ParserTemplate
from myparser.tool import CommonTool


class Kannunu(ParserTemplate):
    HOST = "https://www.kanunu8.com"

    def __init__(self, catalog_url, output_name='all.txt', max_thread_limit=10):
        super().__init__(catalog_url, output_name, max_thread_limit)

    @staticmethod
    def _parse_detail(content):
        """
        解析页面详细内容，提取并返回 标题+正文
        :param content:  小说内容页面
        :return: 标题+正文
        """
        doc = pq.PyQuery(content)
        title = doc('tr:nth-child(1) > td > strong > font').text()
        content = doc('td:nth-child(2) > p').text()
        if '' == title:
            # 模式1未能获取标题，采用模式2
            title = doc('#Article > h1').text()
            title = title.split('\n')[0]
            content = doc('#Article > div > p:not([align])').text()
            content = content.replace('  ', '\n')

        return title, content

    def _parse_catalog(self):
        """
        请求self.url，获取小说目录页面内容
        :return: 所有详细页面的链接
        """
        result = CommonTool.fetch_page(self.catalog_url)
        doc = pq.PyQuery(result)
        # 内存去重
        detail_urls = set()
        # 模式1 https://www.kanunu8.com/book3/8257/
        for a in doc('table:nth-child(2) > tbody > tr > td > a').items():
            detail_url = urllib.request.urljoin(self.catalog_url, a.attr.href)
            if detail_url in detail_urls:
                # 去重
                continue
            if self.HOST not in detail_url:
                # 不是该站点链接
                continue
            detail_urls.add(detail_url)
        # 模式2 https://www.kanunu8.com/book2/10946/index.html
        for a in doc('div.col-left > div > dl > dd > a').items():
            detail_url = urllib.request.urljoin(self.catalog_url, a.attr.href)
            if detail_url in detail_urls:
                # 去重
                continue
            if self.HOST not in detail_url:
                # 不是该站点链接
                continue
            detail_urls.add(detail_url)
        return detail_urls
