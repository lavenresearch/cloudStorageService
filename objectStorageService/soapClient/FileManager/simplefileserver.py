# -*- coding: utf-8 -*-
from socket import *
import os
import struct
import sys

def sendfile(filepath,savepath,ip,port):
    ADDR = (ip,port)
    BUFSIZE = 1024*1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    sendSock = socket(AF_INET,SOCK_STREAM)
    sendSock.connect(ADDR)
    print type(savepath)
    savepath=str(savepath)
    fhead=struct.pack('128s11I',savepath,0,0,0,0,0,0,0,0,os.stat(filepath).st_size,0,0)
    sendSock.send(fhead)
    fp = open(filepath,'rb')
    while 1:
        filedata = fp.read(BUFSIZE)
        #sys.stdout.write('\r%.2f%%' % per)
        #sys.stdout.flush()
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
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

def recvfile(path,iface,port):
    ip=get_ip_address(iface)
    ADDR = (ip,port)
    BUFSIZE = 1024*1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    recvSock = socket(AF_INET,SOCK_STREAM)
    recvSock.bind(ADDR)
    recvSock.listen(True)
    print "等待连接..."
    conn,addr = recvSock.accept()
    print "已连接—> ",addr
    fhead = conn.recv(FILEINFO_SIZE)
    filepath,temp1,filesize,temp2=struct.unpack('128s32sI8s',fhead)
    #print filename,temp1,filesize,temp2
    #print filepath,len(filepath),type(filepath)
    #print filesize
    #filepath = 'new_'+filename.strip('\00') #...
    filename=os.path.basename(filepath).strip('\00')
    if os.path.isfile(os.path.join(path,filename)):
        filename='new_'+filename
    filename=os.path.join(path,filename)

    fp = open(filename,'wb')
    restsize = filesize
    print "正在接收文件... ",
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
    print "接收文件完毕，正在断开连接..."
    fp.close()
    conn.close()
    recvSock.close()
    print "连接已关闭..."

if __name__=='__main__':
    sendfile('/home/allen/Downloads/wps.deb','./wp.deb','115.156.209.190',8001)
