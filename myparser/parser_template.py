import threading
import time
import threadpool
import logging

from myparser.tool import CommonTool
from myparser.defined_exceptions import FetchFailedException, EmptyContentException


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
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def _print_progress(self):
        """
        显示任务进度
        :return:
        """
        ratio = 100 * self.progress_cnt // self.all_chapter_num
        print('[{done:<100}]{cnt}/{all}'.format(done='#' * ratio,
                                                cnt=self.progress_cnt,
                                                all=self.all_chapter_num))

    def start(self):
        """
        解析目录页 尝试爬取所有章节 暂存至temp文件夹
        校验下载完整后，合成小说文件
        若下载不完整，则退出。 使用 --fix=true 参数进入修复模式
        :return:
        """
        start_time = time.time()
        # 先清除临时文件
        CommonTool.clean_temp()
        # 获取所有详细内容链接
        detail_urls = self._parse_catalog()
        self.logger.info("Get novel chapters: " + str(len(detail_urls)))
        self.all_chapter_num = len(detail_urls)
        # 使用threadpool 控制多线程数量
        requests = threadpool.makeRequests(self._get_detail, detail_urls)
        [self.pool.putRequest(req) for req in requests]
        # 等待所有章节抓取完成
        self.pool.wait()

        retry_max = 3
        retry_cnt = 0
        # 进行3次重试， 若无法下载完整，使用 --fix 模式
        while (self.progress_cnt < self.all_chapter_num) and (retry_cnt < retry_max):
            retry_cnt += 1
            self.logger.info("Retry failed set. Len: " + str(len(self.failed_set)))
            retry, self.failed_set = self.failed_set, set()
            requests = threadpool.makeRequests(self._get_detail, retry)
            [self.pool.putRequest(req) for req in requests]
            # 等待所有章节抓取完成
            self.pool.wait()

        self.logger.info("Checking download completeness...")
        if CommonTool.check_completion(detail_urls):
            # 合并全文
            self.logger.info("All chapters are downloaded successfully. Start merging ...")
            CommonTool.merge_all_chapters(self.output_name)
            self.logger.info("Merged. Enjoy reading!")
        else:
            self.logger.error("Some chapters download failed.")
            self.logger.error("Try python novel_download.py -url URL --fix")
        self.logger.info("Total cost %.2fs" % (time.time() - start_time))

    def fix_mode(self):
        """
        修复模式，检查temp文件夹下内容 与 小说目录页 下载未完成章节并合成小说
        :return:
        """
        start_time = time.time()
        self.logger.info("------------------Fix Mode------------------")
        # 获取所有详细内容链接
        detail_urls = self._parse_catalog()
        redownload_urls = CommonTool.get_not_downloaded_chapters(detail_urls)
        self.logger.debug("redownload: " + redownload_urls)
        self.logger.info("Get novel chapters: " + str(len(redownload_urls)))
        self.all_chapter_num = len(redownload_urls)
        # 使用threadpool 控制多线程数量
        requests = threadpool.makeRequests(self._get_detail, redownload_urls)
        [self.pool.putRequest(req) for req in requests]
        # 等待所有章节抓取完成
        self.pool.wait()

        self.logger.info("Checking download completeness...")
        if CommonTool.check_completion(detail_urls):
            # 合并全文
            self.logger.info("All chapters are downloaded successfully. Start merging ...")
            CommonTool.merge_all_chapters(self.output_name)
            self.logger.info("Merged. Enjoy reading!")
        else:
            self.logger.error("Some chapters download failed.")
            self.logger.error("Try: python novel_download.py -url URL -t THREAD_LIMIT --fix=true")
        self.logger.info("Total cost %.2fs" % (time.time() - start_time))

    def _get_detail(self, detail_url):
        """
        获取详细章节详细内容 并写入 temp文件夹下 暂存
        :param detail_url:  章节链接
        :return: None
        """
        time.sleep(0.5)
        try:
            # this will raise FetchFailedException
            content = CommonTool.fetch_page(detail_url)
            # this will raise EmptyContentException
            result = self._check_parse_detail(content)
            # 小说章节末尾链接作为临时储存文件名
            filename = detail_url.split('/')[-1]
            # 暂存章节至文件
            CommonTool.save_chapter(filename, result)
            if self.lock.acquire():
                self.progress_cnt += 1
                self.lock.release()
                self._print_progress()
        except FetchFailedException as e:
            self.failed_set.add(detail_url)
            self.logger.debug("Fetch failed: " + detail_url + ". " + str(e))
        except EmptyContentException:
            self.failed_set.add(detail_url)
            self.logger.debug("Empty content: " + detail_url)

    def _check_parse_detail(self, content):
        """
        调用 _parse_detail 获取章节标题和内容 并进行检查。
        若标题或内容为空 则触发 EmptyContentException
        :param content: 网页html代码
        :return: 小说章节  标题+内容
        """
        title, content = self._parse_detail(content)
        if (title is None) or (title == ""):
            raise EmptyContentException()
        if (content is None) or (content == ""):
            raise EmptyContentException()
        return title + '\n' * 3 + content

    @staticmethod
    def _parse_detail(content):
        """
        解析页面详细内容，提取并返回 标题+正文
        :param content:  小说内容页面
        :return: 标题，正文
        """
        raise NotImplementedError

    def _parse_catalog(self):
        """
        解析目录页面，提取所有章节链接
        :return:  小说章节链接 列表
        """
        raise NotImplementedError
