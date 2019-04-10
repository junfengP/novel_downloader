import threading
import time
import urllib.error
import threadpool

from myparser.tool import CommonTool


class ParserTemplate:
    HOST = None
    lock = threading.Lock()
    progress_cnt = 0
    all_chapter_num = 0
    failed_set = set()

    def __init__(self, catalog_url, output_name='all.txt', max_thread_limit=10):
        self.catalog_url = catalog_url
        self.output_name = output_name
        self.pool = threadpool.ThreadPool(max_thread_limit)

    def _print_progress(self):
        ratio = 100 * self.progress_cnt // self.all_chapter_num
        print('[{done}{notdone}]{cnt}/{all}'.format(done='#' * ratio,
                                                    notdone=' ' * (100 - ratio),
                                                    cnt=self.progress_cnt,
                                                    all=self.all_chapter_num))

    def start(self):
        start_time = time.time()
        # 先清除临时文件
        CommonTool.clean_temp()
        # 获取所有详细内容链接
        detail_urls = self._parse_catalog()
        print("Get novel chapters: " + str(len(detail_urls)))
        self.all_chapter_num = len(detail_urls)
        # 使用threadpool 控制多线程数量
        requests = threadpool.makeRequests(self._get_detail, detail_urls)
        [self.pool.putRequest(req) for req in requests]
        # 等待所有章节抓取完成
        self.pool.wait()
        while self.progress_cnt < self.all_chapter_num:
            print("Retry failed set. Len: " + str(len(self.failed_set)))
            retry, self.failed_set = self.failed_set, set()
            requests = threadpool.makeRequests(self._get_detail, retry)
            [self.pool.putRequest(req) for req in requests]
            # 等待所有章节抓取完成
            self.pool.wait()
        # 合并全文
        CommonTool.merge_all_chapters(self.output_name)
        print("novel download finished!")
        print("Total cost %.2fs" % (time.time() - start_time))

    def _get_detail(self, detail_url):
        # print(detail_url)
        time.sleep(0.5)
        try:
            content = CommonTool.fetch_page(detail_url)
            result = self._parse_detail(content)
            # 小说章节末尾链接作为临时储存文件名
            filename = detail_url.split('/')[-1]
            # 暂存章节至文件
            CommonTool.save_chapter(filename, result)
            if self.lock.acquire():
                self.progress_cnt += 1
                self.lock.release()
                self._print_progress()
        except urllib.error.HTTPError:
            self.failed_set.add(detail_url)

    @staticmethod
    def _parse_detail(content):
        """
        解析页面详细内容，提取并返回 标题+正文
        :param content:  小说内容页面
        :return: 标题+正文
        """
        raise NotImplementedError

    def _parse_catalog(self):
        raise NotImplementedError
