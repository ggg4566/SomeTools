#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org


try:
    from functools import partial
    import sys
    import socket
    import time
    from multiprocessing.dummy import Pool as ThreadPool
    from multiprocessing.dummy import Lock
    import optparse
    import traceback
    from thirdparty import hackhttp
    import codecs
    import re
except Exception,e:
    pass


reload(sys)
sys.setdefaultencoding('utf8')

headers = {
                'content-type': 'charset=utf-8',
                'Accept-Encoding':'gzip, deflate',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
            }
hh = hackhttp.hackhttp(hackhttp.httpconpool(500))
mutex = Lock()


def put_file_contents(filename,contents):
    with open(filename,"ab+") as fin:
        fin.write(contents+'\n')


def get_file_content(filename):
    try:
        result = []
        f = open(filename, "r")
        for line in f.readlines():
            result.append(line.strip())
        f.close()
    except Exception,e:
        print e.message
        sys.exit(0)
    return result


def put_file_contents(filename,contents):
    file = codecs.open(filename,'a',encoding='utf-8')
    file.write(contents+'\n'.decode('utf-8'))
    file.close()


def check_url(url, enable_ssl=False):
    if (not url.startswith("http")):
        if enable_ssl:
            url = 'https://' + url
        else:
            url = 'http://' + url
    return url


def run(action,url):
    info = '-' * 60 + '\n'
    info += u'[-] 正在扫描地址: {} '.format(
                                          url) + '\n'
    print(info)
    try:
        if action == 'get_title':
            res =  get_info(url)
            if res:
                mutex.acquire()
                put_file_contents("out_titles.txt",res)
                mutex.release()
        if action == 'get_www':
            res =  find_www(url)
            if res:
                mutex.acquire()
                put_file_contents("out_www.txt",res)
                mutex.release()
    except Exception as e:
        print(e.message)
        traceback.print_exc()
        pass


def find_www(url):
    found_url = ""
    con_url = check_url(url)
    try:
        status_code, head, content, redirect, log = hh.http(con_url, headers=headers, timeout=5)
        if status_code == 200:
            found_url = con_url
        else:
            con_url = check_url(url,True)
            status_code, head, content, redirect, log = hh.http(con_url, headers=headers, timeout=5)
            if status_code == 200:
                found_url = con_url
    except Exception as e:
        print e.message
    if found_url:
        print("FoundWWW:%s"% found_url)
    return found_url


def get_info(url):
    banner = ""
    try:
        status_code, head, content, redirect, log=hh.http(url,headers=headers,timeout=5)
        temp = head.strip('\r\n').split('\r\n')
        header = dict([s.split(':',1) for s in temp])
        status = status_code
        title = "None"
        data = content
        '''
        soup = beautifulsoup.BeautifulSoup(data, 'html.parser')
        hread = soup.find_all('head')
        _soup = beautifulsoup.BeautifulSoup(str(hread), 'html.parser')
        title = _soup.find('title').string
        '''
        title = re.search(r'<title>(.*?)</title>', data)  # get the title
        try:
            if title:
                # title = title.encode('utf-8').decode('utf-8').strip().strip("\r").strip("\n")[:30]
                title = title.group(1).encode('utf-8').decode('utf-8').strip().strip("\r").strip("\n")[:30]
            else:
                title = "None"
        except Exception,e:
            pass
        banner = "%s||%s||%s||"%(url,status,title)
        if header['Server']:
              banner += header['Server'] #get the server banner
        elif headers['X-Powered-By']:
              banner += header['X-Powered-By']
        print banner
    except Exception,e:
        print e.message
    return banner


def start_task(urls,th_num,action):
    start_time = time.time()
    try:
        # 线程数
        pool = ThreadPool(processes=th_num)
        # get传递超时时间，用于捕捉ctrl+c
        pool.map(partial(run,action), urls)
        pool.close()
        pool.join()
    except Exception as e:
        print e
    except KeyboardInterrupt:
        print(u'\n[-] 用户终止扫描...')
        sys.exit(1)
    print '%d second'% (time.time()-start_time)


def main():
    commandList = optparse.OptionParser('usage: %prog -u URL [-f urls.txt]')
    commandList.add_option('-u', '--url', action="store",
              help="Insert TARGET URL: http[s]://www.victim.com[:PORT]",
            )
    commandList.add_option('-t', '--threads', action="store", default=50, type="int",
                           help="set scan thread number")
    commandList.add_option('-F','--infile',action='store',
                           help='Insert domain filename  ::')
    commandList.add_option('-m', '--action', action='store',
                           help='set function options [get_www,get_title] ::',default = "get_www")
    options, remainder = commandList.parse_args()
    if not options.url and not options.infile:
        commandList.print_help()
        sys.exit(1)
    if options.url:
        urls = [options.url]
    if options.infile:
        urls = get_file_content(options.infile)
    threads = options.threads
    action = options.action
    # urls =['http://phpmyadmin.org/','http://phpmyadmin.org/']
    start_task(urls,threads,action)


if '__main__' == __name__:
    main()