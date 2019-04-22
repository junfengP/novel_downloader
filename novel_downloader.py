#!/usr/bin/env python
# encoding: utf-8
"""
@author: junfeng
@contact: junfeng_pan96@qq.com
@file: novelDownloader.py
@time: 2019/4/10 12:27
@desc:
"""
import argparse
from myparser.config import SUPPORTED_WEBSITE, MAP_CLASS
import logging.config

def main():
    logging.config.fileConfig('logger.conf')
    ap = argparse.ArgumentParser()
    ap.add_argument('-url', required=True, help="URL of novel catalog")
    ap.add_argument('-o', '--output', type=str, default="all.txt", help="Output filename. Default: all.txt")
    ap.add_argument('-t', '--thread-limit', type=int, default=1, help="Thread limit. Default: 1")
    ap.add_argument('--fix', type=bool, default=False,
                    help="When missing chapters use this argument to fix. --fix=true")

    args = vars(ap.parse_args())
    url = args.get('url')
    output = args.get('output')
    thread_limit = args.get('thread_limit')
    fix = args.get('fix')

    solution = None
    for web in SUPPORTED_WEBSITE:
        if web in url:
            solution = MAP_CLASS.get(web)
    if solution is None:
        logging.fatal("Sorry, the url website is not supported yet.")
    else:
        novel = solution(catalog_url=url, output_name=output, max_thread_limit=thread_limit)
        if fix:
            novel.fix_mode()
        else:
            novel.start()


if __name__ == '__main__':
    main()
