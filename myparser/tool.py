import copy
import gzip
import logging
import os
from fake_useragent import UserAgent
import re
import shutil
import socket
import time
import urllib.error
import urllib.request
import os.path

from myparser.defined_exceptions import FetchFailedException


class CommonTool:
    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
    }

    TEMP_DIR = os.path.join(os.curdir, "temp")
    RETRY_TIMES = 3

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler)

    UA = UserAgent()


    @classmethod
    def fetch_page(cls, url):
        """
        请求URL页面内容
        :param url:  待请求网址
        :return:  页面内容
        """
        time.sleep(0.2)
        retry_cnt = 0
        # 重复尝试 获取页面
        data = None
        while retry_cnt < cls.RETRY_TIMES:
            try:
                # 随机选择UA
                headers = copy.deepcopy(cls.HEADERS)
                headers['User-Agent'] = cls.UA.random
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=8)
                data = response.read()
                break
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
                retry_cnt += 1
                time.sleep(1)
                # 失败已达最大次数
                if not (retry_cnt < cls.RETRY_TIMES):
                    raise FetchFailedException(e)
        # 尝试解码数据
        try:
            result = gzip.decompress(data).decode('gbk')
        except UnicodeDecodeError:
            result = gzip.decompress(data).decode('utf-8')
        except OSError:
            try:
                result = data.decode('gbk')
            except UnicodeDecodeError:
                result = data.decode('utf-8')
        return result

    @classmethod
    def save_chapter(cls, filename, content):
        """
        保存章节目录至临时文件
        :param filename:  储存名字，以小说详细页面URL结尾字符串为储存名
        :param content:   存入文件的内容
        :return:  无
        """
        if not os.path.exists(cls.TEMP_DIR):
            os.mkdir(cls.TEMP_DIR)
        with open(os.path.join(cls.TEMP_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(content)

    @classmethod
    def clean_temp(cls):
        """
        清理临时文件
        :return:
        """
        if os.path.exists(cls.TEMP_DIR):
            shutil.rmtree(cls.TEMP_DIR)

    @classmethod
    def merge_all_chapters(cls, output_name):
        """
        将所有章节合并成为一个完整小说文档
        :return:  无
        """
        with open(output_name, 'w', encoding='utf-8') as f:
            # 修复ubuntu下 文件默认排序是按照时间排序的bug
            for chapter in sorted(os.listdir(cls.TEMP_DIR)):
                with open(os.path.join(cls.TEMP_DIR, chapter), 'r', encoding='utf-8') as c:
                    f.write(c.read())
                    f.write('\n\n')

    @classmethod
    def fix_title(cls, title):
        """
        修复章节目录的标题 缺少 第 章，无法被手机阅读器识别章节。
        :param title: 小说章节标题
        :return: 第XXX章 XXXXXXXX
        """
        pattern = r"第\d+章.*"
        if re.match(pattern, title):
            # 标题格式正确，无需修复
            return title
        # 匹配 xxxx yyyy 这类标题， xxxx代表数字
        pattern = r"(\d+)(.*)"
        result = re.match(pattern, title)
        if result:
            chapter_no = result.group(1)
            chapter_title = result.group(2)
            fix_title = "第%s章%s" % (chapter_no, chapter_title)
            return fix_title
        # 匹配 xyzf 第xxx章 yyyy  这类标题，标题前有垃圾
        pattern = r".*(第.*章.*)"
        result = re.match(pattern, title)
        if result:
            title = result.group(1)
        # 无法修复格式
        return title

    @classmethod
    def check_completion(cls, catalog_list):
        # 返回值 确定下载是否完整
        flag = True
        # 获得已下载章节链接尾缀
        downloaded = os.listdir(cls.TEMP_DIR)

        # 检验文件大小 是否 0B
        for f in downloaded:
            f = os.path.join(cls.TEMP_DIR, f)
            # 空文件 则说明下载不完整
            if 0 == os.path.getsize(f):
                flag = False
                # 删除空文件
                os.remove(f)
                cls.logger.debug("remove: " + f)

        # 去除空文件后 重新获得 已下载章节连接尾缀
        downloaded = os.listdir(cls.TEMP_DIR)

        # 章节数量不对等 说明缺失章节
        if len(downloaded) < len(catalog_list):
            cls.logger.debug("download:{d}, catalog:{c}"
                             .format(d=len(downloaded),
                                     c=len(catalog_list)))
            flag = False

        return flag

    @classmethod
    def get_not_downloaded_chapters(cls, catalog_list):
        result = list()
        # 获得已下载章节链接尾缀
        downloaded = os.listdir(cls.TEMP_DIR)
        # 检查各个章节链接是否已经下载
        for u in catalog_list:
            # 该章节 未下载
            if u.split(r'/')[-1] not in downloaded:
                result.append(u)

        return result
