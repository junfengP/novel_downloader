# 小说爬虫助手

> 如果喜欢小说，请支持正版！支持小说作者！

从盗版小说网站，将需要的小说所有章节打包下载。
目前已支持：
- www.biquge5200.cc
- www.booktxt.net (不推荐)
- www.quanshuwang.com (推荐)
- www.kanunu8.com

推荐追小说方法：
使用爬虫下载所有章节，同时RSS订阅该小说。

## 安装方法
本项目基于python3.6.5，其他版本未测试，不兼容python2。
目前暂时只在Win10环境下测试，其他系统下暂未测试。

**1. git clone**
```
git clone https://github.com/junfengP/novel_downloader.git
```

**2. 安装依赖**
```
pip install -r requirements.txt
```

## 运行

```
python3 novel_downloader.py -url 小说目录页 
```

## 参数说明
```
usage: novel_downloader.py [-h] -url URL [-o OUTPUT] [-t THREAD_LIMIT]
                           [--merge MERGE]

optional arguments:
  -h, --help            show this help message and exit
  -url URL              URL of novel catalog
  -o OUTPUT, --output OUTPUT
                        Output filename. Default: all.txt
  -t THREAD_LIMIT, --thread-limit THREAD_LIMIT
                        Thread limit. Default: 1
  --merge MERGE         To merge all chapters into a file.
```