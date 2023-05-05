#! /usr/bin/env python
# -*- coding:utf-8 -*-

import optparse
import sys  
import execjs

reload(sys)  
sys.setdefaultencoding("utf-8")


def get_file_contents(filename):
	contents=""
	with open(filename,"rb") as fin:
		contents=fin.read()
	return contents

def put_file_contents(filename,contents):
	with open(filename,"wb+") as fin:
		fin.write(contents)

def read_origi_pass(pass_file):
	result=[]
	f = open(pass_file, "r")  
	for line in f.readlines():  
		result.append(line.strip()) 
	f.close()
	return result

def  generage_new_password(js_runtime,original_password):
	result=[]
	for i in range(len(original_password)):
		new_password = js_runtime.call('encrypt','admin',original_password[i])
		print new_password
		result.append(new_password)
	return result
if '__main__' == __name__:
	commandList = optparse.OptionParser('usage: %prog -L password.txt')
	commandList.add_option('-L', '--passfile',action="store",
		                            help="Insert password file"
		                          )
	options, remainder = commandList.parse_args()
	if not options.passfile:
		commandList.print_help()
		sys.exit(1)
	passfile = options.passfile
	js= get_file_contents('js/encry.js')
	js_runtime=execjs.compile(js)
	original_password = read_origi_pass(passfile)
	new_password=generage_new_password(js_runtime,original_password)
	passwords = '\n'.join(new_password)
	put_file_contents('new_password.txt',passwords + '\n')	
	print 'encrypted passwords alread save new_passwords.txt!!!\n'	
