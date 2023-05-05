#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org

from mitmproxy import http
from urllib import parse
import requests
from requests.adapters import HTTPAdapter

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
           'Connection': 'close'}

req = requests.session()
req.mount('http://', HTTPAdapter(max_retries=3))
req.mount('https://', HTTPAdapter(max_retries=3))

req.headers = headers
url = 'http://127.0.0.1:5000/'


def q_str_to_dict(query_str): #input id=1&name=greent | output {'id':1,'name':'greent'}
    data={}
    try:
        data= dict((k, v if len(v) > 1 else v[0]) for k, v in parse.parse_qs(query_str).items())
    except Exception as e:
        print(e)
    return data


def dict_to_q_str(dict_v):
    data=""
    try:
        node=[k+"="+v for k,v in dict_v.items()]
        data="&".join(node)
    except Exception as e:
        print(e)
    return data


def get_calc_hash(payload):
    ret=""
    con_url = "{0}?payload={1}".format(url,payload)
    ret = req.get(con_url).text
    return ret


def request(flow: http.HTTPFlow) -> None:
    print("mimt_proxy_encry:"+flow.request.url)
    post_data=flow.request.get_text()

    print(post_data)
    dict_v=q_str_to_dict(post_data)
    # encry payload
    dict_v['pwd']= get_calc_hash(dict_v['pwd'])
    print(dict_v['pwd'])

    post_data=dict_to_q_str(dict_v)
    print("POSTDATA Success Modiy :")
    print(post_data)
    flow.request.text = post_data

