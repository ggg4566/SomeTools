#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org
# time:2019/9/21

import requests
import optparse
import sys
import base64
from urllib.parse import quote, unquote
from urllib import parse
from bs4 import BeautifulSoup
from multiprocessing.dummy import Lock
from multiprocessing.dummy import Pool as ThreadPool
import traceback
import warnings
warnings.filterwarnings("ignore")



mutex = Lock()

dork = ""
outfile = ""
search_type = 'www'

headers = {

    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}
session = requests.session()
session.headers = headers
session.timeout = 6
find_urls=[]


def put_file_contents(filename, contents):
    with open(filename, "a+") as fin:
        fin.write(contents + '\n')


def url2host(url):
    _ = parse.urlparse(url)
    netloc = _.netloc
    scheme = _.scheme
    return scheme+'://'+netloc


def get_realurl(target_url):
    try:
        response = session.get(target_url,headers =headers,verify = False)
        realurl = response.url
        return realurl
    except:
        pass
        return ""


def get_www_result(url):
    try:
        r = session.get(url, headers=headers,verify = False)
        text = r.text
        soup = BeautifulSoup(text, 'lxml')
        text = soup.find(attrs={'id': 'content_left'})
        _soup = BeautifulSoup(str(text), 'lxml')
        a_l = _soup.find_all(attrs={'class': 'c-showurl c-color-gray'})
        for v in a_l:
            url = v['href']
            if url:
                r = url2host(get_realurl(url))
                print(r)
                find_urls.append(r)

    except Exception:
        print(traceback.format_exc())
        pass
    return


def baidu_query_mult(all_pages, dork, threads):
    query_keyword = quote(dork)
    urls = []
    pn = int(all_pages / 10) + 1
    for i in range(pn):
        url = 'https://www.baidu.com/s?wd={0}&pn={1}'.format(query_keyword, i * 10)
        urls.append(url)
    try:
        # 线程数
        pool = ThreadPool(processes=threads)
        # get传递超时时间，用于捕捉ctrl+c

        pool.map_async(get_www_result, urls).get(0xffff)
        pool.join()
    except Exception as e:
        pass
    except KeyboardInterrupt:
        print(u'\n[-] 用户终止扫描...')
        sys.exit(1)


def main():
    banner = r'''         

    ██████╗  █████╗ ██╗██████╗ ██╗   ██╗     ██████╗ ██╗   ██╗███████╗██████╗ ██╗   ██╗
    ██╔══██╗██╔══██╗██║██╔══██╗██║   ██║    ██╔═══██╗██║   ██║██╔════╝██╔══██╗╚██╗ ██╔╝
    ██████╔╝███████║██║██║  ██║██║   ██║    ██║   ██║██║   ██║█████╗  ██████╔╝ ╚████╔╝ 
    ██╔══██╗██╔══██║██║██║  ██║██║   ██║    ██║▄▄ ██║██║   ██║██╔══╝  ██╔══██╗  ╚██╔╝  
    ██████╔╝██║  ██║██║██████╔╝╚██████╔╝    ╚██████╔╝╚██████╔╝███████╗██║  ██║   ██║   
    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝      ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   
                                                                                   
    version: 1.0.2
    mailto:root@flystart.org
    '''

    print(banner)
    commandList = optparse.OptionParser(usage='%prog  -q dork [-n limit -t thread_num -o save_result.txt] ',
                                        version='1.0')
    commandList.add_option('-q', '--dork', action='store',
                           help='Insert baidu query dork')
    commandList.add_option('-n', '--limit', action='store', default=50, type=int,
                           help='set search page numbers:defalut:20', )
    commandList.add_option('-t', '--threads', action='store', default=5, type=int,
                           help='Insert query all pages:defalut:20', )
    commandList.add_option('-o', '--outfile', action='store', default="baidu_result.txt",
                           help='Insert save filename. defualt:baidu_result.txt')
    options, remainder = commandList.parse_args()
    global dork, outfile, search_type
    dork = options.dork
    threads = options.threads
    number_page = options.limit
    outfile = options.outfile
    if not dork or not outfile:
        print('\033[1;34m' + banner + '\033[0m')
        commandList.print_help()
        sys.exit(1)
    print(dork)
    baidu_query_mult(number_page, dork, threads)
    global find_urls
    find_urls = list(set(find_urls))
    for v in find_urls:
        put_file_contents(outfile, v)
    return


if __name__ == '__main__':
    main()