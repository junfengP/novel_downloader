import copy
import gzip
import os
import random
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
    USER_AGENT = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
        "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
        "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
        "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
        "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
        "UCWEB7.0.2.37/28/999",
        "NOKIA5700/ UCWEB7.0.2.37/28/999",
        "Openwave/ UCWEB7.0.2.37/28/999",
        "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    ]
    TEMP_DIR = os.path.join(os.curdir, "temp")
    RETRY_TIMES = 3

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
                headers['User-Agent'] = random.choice(cls.USER_AGENT)
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=8)
                data = response.read()
                break
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout):
                retry_cnt += 1
                time.sleep(1)
                # 失败已达最大次数
                if not (retry_cnt < cls.RETRY_TIMES):
                    raise FetchFailedException()
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
                print("remove: " + f)

        # 去除空文件后 重新获得 已下载章节连接尾缀
        downloaded = os.listdir(cls.TEMP_DIR)

        # 章节数量不对等 说明缺失章节
        if len(downloaded) != len(catalog_list):
            print("download:{d}, catalog:{c}".format(d=len(downloaded), c=len(catalog_list)))
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


