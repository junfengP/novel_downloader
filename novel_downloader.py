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
from myparser.tool import CommonTool
from myparser.config import SUPPORTED_WEBSITE, MAP_CLASS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-url', required=True, help="URL of novel catalog")
    ap.add_argument('-o', '--output', type=str, default="all.txt", help="Output filename. Default: all.txt")
    ap.add_argument('-t', '--thread-limit', type=int, default=1, help="Thread limit. Default: 1")
    ap.add_argument('--merge', type=bool, default=False, help="To merge all chapters into a file.")
    args = vars(ap.parse_args())
    url = args.get('url')
    output = args.get('output')
    merge = args.get('merge')
    thread_limit = args.get('thread_limit')
    if merge:
        print("Start merging chapters.")
        CommonTool.merge_all_chapters(output)
        print("Merged. Enjoy reading!")
        exit(0)
    solution = None
    for web in SUPPORTED_WEBSITE:
        if web in url:
            solution = MAP_CLASS.get(web)
    if solution is None:
        print("Sorry, the url website is not supported yet.")
    else:
        novel = solution(catalog_url=url, output_name=output, max_thread_limit=thread_limit)
        novel.start()


if __name__ == '__main__':
    main()