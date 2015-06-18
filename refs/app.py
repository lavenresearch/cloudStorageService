#!/usr/bin/env python
#coding=utf-8

import sys
import random
import MySQLdb
import pymongo
import socket
import os

class ApplyMysql():
    def __init__(self,client_ip,username,password,database):
        self.client_ip=client_ip
        self.client_number=len(self.client_ip) 
        self.username=username
        self.password=password
        self.database=database
        self.root_password='1991922'	
        self.online_database=[]

    def check(self):
        for i in range(0,self.client_number):
            try:
                conn = MySQLdb.connect(host=self.client_ip[i],user='root',passwd=self.root_password,charset='utf8')
                self.online_database.append(self.client_ip[i])
                conn.close()
            except MySQLdb.Error,e:
                #self.is_online.append(False)
                print "Mysql@%s Error %d: %s"% (self.client_ip[i], e.args[0], e.args[1])
        return len(self.online_database)
    
    def choose(self):
	if len(self.online_database)!=0:
	    self.choosed=self.online_database[random.randint(0,len(self.online_database))]
    
    def start(self):
        try:
            conn=MySQLdb.connect(host=self.choosed,user='root',passwd=self.root_password,charset='utf8')
            cur=conn.cursor()
            #conn.select_db('mysql')

            #add a new user
            sql_create_remote_user="insert into mysql.user(Host,User,Password,ssl_cipher,x509_issuer,x509_subject)\
                            values('%%','%s',password('%s'),'','','')"%(self.username,self.password)
            sql_create__local_user="insert into mysql.user(Host,User,Password,ssl_cipher,x509_issuer,x509_subject)\
                            values('localhost','%s',password('%s'),'','','')"%(self.username,self.password)
            db_name=self.username+'_'+self.database
            sql_create_db="create database %s"%(db_name)
            sql_giant="grant all privileges on %s.* to '%s'@'%%' identified by '%s'"%(db_name,self.username,self.password)
            sql_flush="flush privileges"

            cur.execute(sql_create_remote_user)
            cur.execute(sql_create_local_user)
            cur.execute(sql_flush)            
            cur.execute(sql_create_db)
            cur.execute(sql_flush)            
            cur.execute(sql_giant)
            cur.execute(sql_flush)            
            
            conn.commit()
            cur.close()
            conn.close()
            print 'you have just applied for mysql database at %s, your username is %s'%(self.choosed,self.username)

        except MySQLdb.Error,e:
            print "apply for Mysql@%s Error %d: %s" \
                    % (self.choosed, e.args[0], e.args[1])
        
class ApplyMongodb():
    def __init__(self,client_ip,username,password,database):
        self.client_ip=client_ip
        self.client_number=len(self.client_ip)
        self.username=username
        self.password=password
        self.database=database
        
    def check(self):
        self.is_online=[]
        for i in range(0,self.client_number):
            try:
                conn = pymongo.Connection(self.client_ip[i],27017)
                self.is_online.append(True)
            except :
                #self.is_online.append(False)
                print "Mongodb@%s Error!"%(self.client_ip[i])
        return len(self.is_online)
    
    def choose(self):
        self.online_database=[]
    
        for i in range(0,self.client_number):
            if self.is_online[i]==True:
                self.online_database.append(self.client_ip[i])
        self.choosed=self.online_database[random.randint(0,len(self.online_database))]

    def start(self):
        conn=pymongo.Connection(self.choosed,27017)
        conn.__setattr__(self.database,self.database)
        mydb=conn.__getattr__(self.database)
        mydb.add_user(self.username,user.password)
        mydb.authenticate(self.username,user.password)
        print 'you have just apply for mongo database at %s, your username is %s'%(self.choosed,self.username)

def valid_ip(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False
    
def get_all_client_ip(path):
    all_items=os.listdir(path)
    ips=[]
    for item in all_items:
        if os.path.isdir(os.path.join(path,item)) and valid_ip(item):
            ips.append(item)
    return item
    
if __name__=='__main__':
    #if len(sys.argv)==1 len(sys.argv)==2:
    #    print 'error happens, you have not input enough arguments'
    #else:
    #    client_ip=sys.argv[3:]
    #path='rrds/'
    #client_ip=get_all_client_ip(path)
    client_ip=['192.168.16.200']
    database='db'
    my=ApplyMysql(client_ip,'lee','123456',database) 
    if my.check():
        my.choose()
        my.start()    
