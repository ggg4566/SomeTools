#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org
# time:2019/9/21

import requests
import optparse
import sys
import base64
import time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Lock
from multiprocessing.dummy import Pool as ThreadPool

headers = {
                'Accept-Encoding':'gzip, deflate',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
            }

req = requests.session()
req.headers = headers
req.timeout = 10
mutex = Lock()

dork = ""
outfile = ""
def put_file_contents(filename,contents):
    with open(filename,"ab+") as fin:
        fin.write(contents+'\n')


def get_result(html):
    global outfile
    try:
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find_all('div', attrs={'class': 'list_mod_t'})
        _soup = BeautifulSoup(str(div), 'html.parser')
        a= _soup.find_all('a', attrs={'target': '_blank'})
        for v in a:
            url = v['href']
            print url
            put_file_contents(outfile,url)

    except Exception,e:
        print(e.message)
    return


def fofa_query(all_pages,dork):
    ret = ""
    url = "https://fofa.so/result?"
    qbase = base64.b64encode(dork)
    for i in range(1,all_pages+1):
        params = {"page":str(i),"qbase64":qbase}
        try:
            res = req.get(url,params= params,headers=headers)
            text = res.content
            get_result(text)
        except Exception,e:
            print e.message
    return


def fofa_query_sing(page_num):
    global dork
    ret = ""
    url = "https://fofa.so/result?"
    qbase = base64.b64encode(dork)
    params = {"page": str(page_num), "qbase64": qbase}
    try:
        res = req.get(url, params=params, headers=headers)
        text = res.content
        get_result(text)
    except Exception,e:
        print e.message
        pass

def fofa_query_mult(all_pages,dork,threads):
    try:
        # 线程数
        pool = ThreadPool(processes=threads)
        # get传递超时时间，用于捕捉ctrl+c
        l = range(1,all_pages+1)
        pool.map_async(fofa_query_sing,l).get(0xffff)
        pool.close()
        pool.join()
    except Exception as e:
        print e
    except KeyboardInterrupt:
        print(u'\n[-] 用户终止扫描...')
        sys.exit(1)


def main():
    commandList = optparse.OptionParser(usage='%prog -c cookie -q dork [-n pages -t thread_num -o save_result.txt ',
                                      version='1.0')
    commandList.add_option('-c','--cookie',action='store',
                           help='Insert cookie after login fofa')
    commandList.add_option('-q', '--dork', action='store',
                           help='Insert fofa query dork')
    commandList.add_option('-n', '--limit', action='store',default=20,type = int,
                           help='Insert query all pages:defalut:20',)
    commandList.add_option('-t', '--threads', action='store', default=20, type=int,
                           help='Insert query all pages:defalut:20', )
    commandList.add_option('-o','--outfile',action='store',default="fofa_result.txt",
                           help='Insert save filename  ::')
    options,remainder = commandList.parse_args()
    cookie = options.cookie
    global dork,outfile
    dork = options.dork
    threads = options.threads
    print dork
    number_page =options.limit
    outfile = options.outfile
    if not cookie or not dork or not outfile:
        commandList.print_help()
        sys.exit(1)
    dork = dork.decode("GB2312").encode("UTF-8")
    headers['Cookie'] = cookie
    # fofa_query(number_page,dork)
    fofa_query_mult(number_page, dork, threads)
    return


if __name__ == '__main__':
    main()