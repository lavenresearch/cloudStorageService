#!/usr/bin/env python
#coding=utf-8

import sys
import random
import MySQLdb
import pymongo
import socket
import os
import hosts

class ApplyMysql():
    def __init__(self,client_ip,username,password,database):
        self.client_ip=client_ip
        self.client_number=len(self.client_ip) 
        self.username=username
        self.password=password
        self.database=database
        self.root_password='root'	
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
        print 'in choose'
        if len(self.online_database)!=0:
            self.choosed=self.online_database[random.randint(0,len(self.online_database)-1)]
    
    def start(self):
        conn=MySQLdb.connect(host=self.choosed,user='root',passwd=self.root_password,charset='utf8')
        cur=conn.cursor()
        conn.select_db('mysql')
         #add a new user
        sql_create_remote_user="insert into mysql.user(Host,User,Password,ssl_cipher,x509_issuer,x509_subject)\
                        values('%%','%s',password('%s'),'','','')"%(self.username,self.password)
        sql_create_local_user="insert into mysql.user(Host,User,Password,ssl_cipher,x509_issuer,x509_subject)\
                        values('localhost','%s',password('%s'),'','','')"%(self.username,self.password)
        db_name=self.username+'_'+self.database
        sql_create_db="create database %s"%(db_name)
        sql_giant="grant all privileges on %s.* to '%s'@'%%' identified by '%s'"%(db_name,self.username,self.password)
        sql_flush="flush privileges"
        try:
            res = cur.execute(sql_create_remote_user)
            print res
        except MySQLdb.Error,e:
            print "remote user exit!"
        try:
            res = cur.execute(sql_create_local_user)
            print res
        except MySQLdb.Error,e:
            print "remote user exit!"
        cur.execute(sql_flush)
        try:
            res = cur.execute(sql_create_db)
            print res
        except MySQLdb.Error,e:
            print "database exit"
            print "failed"
            return 0
        cur.execute(sql_flush)            
        res = cur.execute(sql_giant)
        print res
        cur.execute(sql_flush)            
        
        conn.commit()
        cur.close()
        conn.close()
        #print 'you have just applied for mysql database at %s, your username is %s'%(self.choosed,self.username)
        print self.username+'@'+self.password+'@'+db_name+'@'+'mysql'+'@'+self.choosed+'@success'
#        except MySQLdb.Error,e:
#            print "apply for Mysql@%s Error %d: %s" \
#                    % (self.choosed, e.args[0], e.args[1])
    def remove(self,hostIP):
        conn = MySQLdb.connect(host=hostIP,user='root',passwd=self.root_password,charset='utf8')
        cur = conn.cursor()
        conn.select_db('mysql')
        deleteDatabase = 'drop database %s'%(self.username+'_'+self.database)
        deleteUser = "drop user '%s'@'%%'"%(self.username)
        try:
            res = cur.execute(deleteDatabase)
            res = cur.execute(deleteUser)
            conn.commit()
            cur.close()
            conn.close()
        except:
            conn.commit()
            cur.close()
            conn.close()
            print "failed"

class ApplyMongodb():
    def __init__(self,client_ip,username,password,database):
        self.client_ip=client_ip
        self.client_number=len(self.client_ip)
        self.username=username
        self.password=password
        self.database=database
        self.online_database=[]
        
    def check(self):
        print 'in check'
        self.is_online=[]
        for i in range(0,self.client_number):
            try:
                client = pymongo.MongoClient(self.client_ip[i],27017)
                self.online_database.append(self.client_ip[i])
		client.close()
            except :
                #self.is_online.append(False)
                print "Mongodb@%s Error!"%(self.client_ip[i])
        return len(self.online_database)
    
    def choose(self):
        print 'in choose'
        if len(self.online_database)!=0:
            self.choosed=self.online_database[random.randint(0,len(self.online_database)-1)]
        print str(self.choosed)

    def start(self):
        client=pymongo.MongoClient(self.choosed,27017)
        admindb = client['admin']
        admindb.authenticate('root','root')
        db_name=self.username+'_'+self.database
        mydb=client[db_name]
        mydb.add_user(self.username,self.password)
        # mydb.authenticate(self.username,self.password)
        client.close()
        # print 'you have just apply for mongo database at %s, your username is %s'%(self.choosed,self.username)
        print self.username+'@'+self.password+'@'+db_name+'@'+'mongodb'+'@'+self.choosed+'@success'
    def remove(self, hostIP):
        client = pymongo.MongoClient(hostIP,27017)
        admindb = client['admin']
        admindb.authenticate('root','root')
        client.drop_database(self.username+'_'+self.database)
        db = client[self.username+'_'+self.database]
        db.remove_user(self.username)
        client.close()
        print "success"

        
 
if __name__=='__main__':
    print '###########################3'
    print sys.argv
    print "#############################"
    if len(sys.argv)!=5:
        print '''error happens, you have not input enough arguments
		for example:
			python apply.py username password dbname database_type
		'''
    #else:
    #    client_ip=sys.argv[3:]
    #path='rrds/'
    #client_ip=get_all_client_ip(path)
    else:      
    	 # clients_ip=['192.168.16.106']
        clients_ip=hosts.get_all_clients_ip('/etc/hosts','/var/lib/ganglia/rrds/client/')
            #database='db'
    print sys.argv[4]
    if sys.argv[4]=='mongodb':
        my=ApplyMongodb(clients_ip,
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]) 
    	    #print clients_ip
    else:
        my=ApplyMysql(clients_ip,
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]) 
    if my.check():
        my.choose()
        my.start()
