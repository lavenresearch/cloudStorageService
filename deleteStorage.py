#coding=utf-8
import sys,os,pymongo,socket,MySQLdb
from getNAS import NASService
from getDB import ApplyMongodb,ApplyMysql

if __name__ == '__main__':
    redisIP = "192.168.12.100"
    redisPort = 6379
    storageType = sys.argv[1]
    if storageType == 'nfs':
        userName = sys.argv[2]
        homeDir = sys.argv[3]
        hostIP = sys.argv[4]
        nfsS = NASService(hostIP,userName,"nopassword",homeDir, redisIP,redisPort)
        nfsS.deleteNFS()
        print "success"
    elif storageType == 'samba':
        nfsS.deletSamba()
        print "success"
    elif storageType == 'mongodb':
        userName = sys.argv[2]
        password = sys.argv[3]
        dbName = sys.argv[4]
        hostIP = sys.argv[5]
        mongodbS = ApplyMongodb([hostIP],userName,password,dbName)
        mongodbS.remove(hostIP)
        print "success"
    elif storageType == 'mysql':
        userName = sys.argv[2]
        password = sys.argv[3]
        dbName = sys.argv[4]
        hostIP = sys.argv[5]
        mysqlS = ApplyMysql([hostIP],userName,password,dbName)
        mysqlS.remove(hostIP)
        print "success"
    else:
        print "error"
