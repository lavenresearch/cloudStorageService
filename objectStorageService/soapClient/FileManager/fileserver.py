#!/usr/bin/env python
#coding=utf-8
from socket import *
import os
import struct
import threading
import sys

def sendfile(filepath,ip,port):
    '''
        send a file 
        args:
            filepath    the full path of a file
                  ip    the ip address you want to send file to
                port    the port you want to send file to      
    '''
    ADDR = (ip,port)
    BUFSIZE = 1024*1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    sendSock = socket(AF_INET,SOCK_STREAM)
    sendSock.connect(ADDR)
    filepath=str(filepath)
    fhead=struct.pack('128s11I',filepath,0,0,0,0,0,0,0,0,os.stat(filepath).st_size,0,0)
    sendSock.send(fhead)
    fp = open(filepath,'rb')
    while 1:
        filedata = fp.read(BUFSIZE)
        if not filedata: break
        sendSock.send(filedata)
    print "文件传送完毕，正在断开连接..."
    fp.close()
    sendSock.close()
    print "连接已关闭..."

def get_ip_address(ifname):#获得本机ip
    import socket
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def recvfile(path,iface,port):
    '''
        recevive a file
        args:
            port    the port used to recevive file
    '''
    myip=get_ip_address(iface)
    ADDR = (myip,port)
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
  
    recvSock = socket(AF_INET,SOCK_STREAM)
    recvSock.bind(ADDR)
    recvSock.listen(True)
    threads=[]
    #print "等待连接..."
    while 1:
        conn,addr = recvSock.accept()
        t=threading.Thread(target=startrecv,args=(path,conn,addr,FILEINFO_SIZE))
        t.setDaemon(True)
        t.start()
        
    #startrecv(recvSock,FILEINFO_SIZE)
    
        
def startrecv(path,conn,addr,FILEINFO_SIZE):

    print "客户端 ",addr[0],"发送文件","端口：",addr[1]
    BUFSIZE = 1024*1024
    fhead = conn.recv(FILEINFO_SIZE)
    filepath,temp1,filesize,temp2=struct.unpack('128s32sI8s',fhead)
        #print filename,temp1,filesize,temp2
        #print filepath,len(filepath),type(filepath)
        #print filesize
        #filepath = 'new_'+filename.strip('\00') #...
    if os.path.exists(os.path.dirname(filepath)):
        filename=filepath.strip('\00')
    else:
        filename=os.path.basename(filepath).strip('\00')
        if os.path.isfile(os.path.join(path,filename)):
            filename='new_'+filename
        filename=os.path.join(path,filename)
    
    fp = open(filename,'wb')
    restsize = filesize
    print "\t",addr[0],":",addr[1],"正在接收文件... "
    while 1:
        if restsize > BUFSIZE:
            filedata = conn.recv(BUFSIZE)
        else:
            filedata = conn.recv(restsize)
        if not filedata: break
        fp.write(filedata)
        restsize = restsize-len(filedata)
        if restsize == 0:
                break
    print "\t",addr[0],":",addr[1],"接收文件完毕，正在断开连接..."
    fp.close()
    conn.close()
    #recvSock.close()
    print "连接已关闭..."

if __name__=='__main__':
    savepath=str('./')
    
    recvfile(savepath,'eth0',8001)
