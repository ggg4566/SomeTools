#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org
# time:2019/9/21

import requests
import optparse
import sys
import base64
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
search_type ='www'
def put_file_contents(filename,contents):
    with open(filename,"ab+") as fin:
        fin.write(contents+'\n')


def get_www_result(html):
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


def get_host_result(html):
    global outfile
    try:
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find_all('div', attrs={'class': 'list_mod_t'})
        _soup = BeautifulSoup(str(div), 'html.parser')
        a = _soup.find_all('div', attrs={'class': 'ip-no-url'})
        if a:
            for host in a:

                host = (host.string).replace(r'\n','').strip()
                print(host)
                put_file_contents(outfile,host)

    except Exception,e:
        print(e.message)
    return


def fofa_query(all_pages,dork):
    global search_type
    ret = ""
    url = "https://fofa.so/result?"
    qbase = base64.b64encode(dork)
    for i in range(1,all_pages+1):
        params = {"page":str(i),"qbase64":qbase}
        try:
            res = req.get(url,params= params,headers=headers)
            text = res.content
            if search_type =='www':
                get_www_result(text)
            if search_type == 'host':
                get_host_result(text)
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
        if search_type == 'www':
            get_www_result(text)
        if search_type == 'host':
            get_host_result(text)
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
    banner = '''         
   ___       ___        ___ _          __
  / _/___   / _/___ _  / _/(_)___  ___/ /
 / _// _ \ / _// _ `/ / _// // _ \/ _  / 
/_/  \___//_/  \_,_/ /_/ /_//_//_/\_,_/  
                                         
            version: 1.0.2
            mailto:root@flystart.org
    '''

    commandList = optparse.OptionParser(usage='%prog -c cookie -q dork [-n pages -t thread_num -o save_result.txt ',
                                      version='1.0')
    commandList.add_option('-c','--cookie',action='store',
                           help='Insert cookie after login fofa')
    commandList.add_option('-q', '--dork', action='store',
                           help='Insert fofa query dork')
    commandList.add_option('-n', '--limit', action='store',default=20,type = int,
                           help='set search page numbers:defalut:20',)
    commandList.add_option('-s', '--type', action='store', default='www',
                           help='set search search type.[www|host] default:www' )
    commandList.add_option('-t', '--threads', action='store', default=20, type=int,
                           help='Insert query all pages:defalut:20', )
    commandList.add_option('-o','--outfile',action='store',default="fofa_result.txt",
                           help='Insert save filename. defualt:fofa_result.txt')
    options,remainder = commandList.parse_args()
    cookie = options.cookie
    global dork,outfile,search_type
    dork = options.dork
    search_type = options.type
    threads = options.threads
    number_page =options.limit
    outfile = options.outfile
    if not cookie or not dork or not outfile:
        print('\033[1;34m' + banner + '\033[0m')
        commandList.print_help()
        sys.exit(1)
    dork = dork.decode("GB2312").encode("UTF-8")
    headers['Cookie'] = cookie
    # fofa_query(number_page,dork)
    print(dork)
    fofa_query_mult(number_page, dork, threads)
    return


if __name__ == '__main__':
    main()