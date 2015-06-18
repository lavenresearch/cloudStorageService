#!/usr/bin/env python
#coding=utf-8

import sys
import random
import MySQLdb
# import pymongo
import socket
import os

class DatabaseInit():
    def __init__(self,clients,database_type):
        self.clients=clients
        self.client_number=len(self.clients)
        #self.rootname=username
        #self.root_password=root_password
        self.online_database={}
	self.database_type=database_type

    def check(self):
	if self.database_type=='mysql':
	    for i in self.clients:
	        try:
                    conn = MySQLdb.connect(host=i,user=self.clients[i][0],passwd=self.clients[i][1],charset='utf8')
                    self.online_database[i]=self.clients[i]
                    conn.close()
                except MySQLdb.Error,e:
                    #self.is_online.append(False)
                    print "Mysql@%s Error %d: %s"% (i, e.args[0], e.args[1])
            return len(self.online_database)
	else:
	    return 0
    
    def start(self):
	if self.database_type=='mysql':
	    for i in self.online_database:
	        try:
                    conn=MySQLdb.connect(host=i,user=self.online_database[i][0],passwd=self.online_database[i][1],charset='utf8')
                    cur=conn.cursor()
                    #conn.select_db('mysql')

                    #add a new user
                    sql_set_root_password="update mysql.user set password=password('root') where user='root'"

                    sql_set_remote_access="update mysql.user set host='%' where user='root' and host='127.0.0.1'"
                    sql_flush="flush privileges"

                    cur.execute(sql_set_root_password)
                    cur.execute(sql_flush)            
                    cur.execute(sql_set_remote_access)
                    cur.execute(sql_flush)            
            
                    conn.commit()
                    cur.close()
                    conn.close()
                    print 'initial database %s on %s ok! '%(self.database_type,i)

                except MySQLdb.Error,e:
                    print "initial databse %s on %s error! %d: %s" \
                        % (self.database_type,i, e.args[0], e.args[1])
    
if __name__=='__main__':
    #if len(sys.argv)==1 len(sys.argv)==2:
    #    print 'error happens, you have not input enough arguments'
    #else:
    #    client_ip=sys.argv[3:]
    #path='rrds/'
    #client_ip=get_all_client_ip(path)
    '''clients={'192.168.16.101':('root',''),
		'192.168.16.102':('root',''),
	        '192.168.16.103':('root',''),
		'192.168.16.104':('root',''),
		'192.168.16.105':('root',''),
		'192.168.16.106':('root','')}
    '''
    clients={'localhost':('root','')} 
    database='mysql'
    my=DatabaseInit(clients,database) 
    if my.check():
        my.start()    
