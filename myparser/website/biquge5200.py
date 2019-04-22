import pyquery.pyquery as pq

from myparser.defined_exceptions import EmptyContentException
from myparser.parser_template import ParserTemplate
from myparser.tool import CommonTool


class Biquge5200(ParserTemplate):
    HOST = "https://www.biquge5200.cc"

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
        title = doc('#wrapper > div.content_read > div > div.bookname > h1').text()
        title = CommonTool.fix_title(title)
        content = doc('#content').text()
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
        for a in doc('#list > dl > dd > a').items():
            detail_url = a.attr.href
            if detail_url in detail_urls:
                # 去重
                continue
            if self.HOST not in detail_url:
                # 不是该站点链接
                continue
            detail_urls.add(detail_url)
        return detail_urls
