#!/usr/bin/env python
#coding=utf-8
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
import os
import os.path
import shutil
import time, datetime
import fileserver
import threading
import hashlib
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
current_path = '/'


_FILE_SLIM = (5*1024*1024) # 100MB


def file_md5(filename):
    global _FILE_SLIM
    calltimes = 0
    hmd5 = hashlib.md5()
    fp = open(filename,"rb")
    f_size = os.stat(filename).st_size
    if f_size>_FILE_SLIM:
        while(f_size>_FILE_SLIM):
            hmd5.update(fp.read(_FILE_SLIM))
            f_size/=_FILE_SLIM
            calltimes += 1   #delete
        if(f_size>0) and (f_size<=_FILE_SLIM):
            hmd5.update(fp.read())
    else:
        hmd5.update(fp.read())
    return (hmd5.hexdigest(),calltimes)

def AbsolutePath(FileOrPath):
    global current_path
    FileOrPath=str(FileOrPath)
    if FileOrPath[0] == '/':
        return FileOrPath
    elif FileOrPath[:2]=='./':
        return os.path.join(current_path,FileOrPath[2:])
    else:
        #if current_path[-1] != '/':
        #    current_path = current_path + '/'
        #FullPath = current_path + FileOrPath
        return os.path.join(current_path,FileOrPath)
def pwd():
    return current_path

def rm(filename):
    fname = AbsolutePath(filename)
    if os.path.isfile(fname):
        os.remove(fname)
        return True
    else:
        return False


def cp(src, dest):
    FileSrc = AbsolutePath(src)
    FileDest = AbsolutePath(dest)
    size = 1048576
    fsrc = open(FileSrc, 'rb')
    if not os.path.exists(FileDest):
        fdest = open(FileDest, 'wb')
        buf = fsrc.read(size)
        while buf:
            fdest.write(buf)
            buf = fsrc.read(size)

        fsrc.close()
        fdest.close()
        return True


def rename(src, dest):
    FileSrc = AbsolutePath(src)
    FileDest = AbsolutePath(dest)
    os.rename(FileSrc, FileDest)
    return True


def ls_dir(path):
    AbPath = AbsolutePath(path)
    all_list = os.listdir(AbPath)
    dir_list = []
    for name in all_list:
        FullName = os.path.join(AbPath, name)
        if os.path.isdir(FullName):
            dir_list.append(name)

    return dir_list


def ls_file(path):
    AbPath = AbsolutePath(path)
    all_list = os.listdir(AbPath)
    file_list = []
    for name in all_list:
        FullName = os.path.join(AbPath, name)
        if os.path.isfile(FullName):
            file_list.append(name)
    return file_list


def mkdir(path):
    AbPath = AbsolutePath(path)
    os.mkdir(AbPath)
    return True


def rmdir(path):
    AbPath = AbsolutePath(path)
    os.rmdir(AbPath)
    return True


def getsize(filename):
    #print str(filename)
    FullName = AbsolutePath(filename)
    return os.path.getsize(FullName)


def sendfile():
   # path='./'
   # recvfile(path,'eth0',8001)
    pass


def getfile(filename,ip,port):
    filename=str(filename)
    ip=str(ip)
    port=int(port)
    filename = AbsolutePath(filename)
    md5=file_md5(filename)
    print ip
    print type(filename)
    fileserver.sendfile(filename,ip,port)
    return md5[0]

def cd(path):
    global current_path
    if path[0] == '/':
        if not os.path.isdir(path):
            return False
        else:
            current_path = path
            if current_path[-1] != '/':
                current_path = current_path + '/'
            return True
    else:
        if current_path[-1] != '/':
            current_path = current_path + '/'
        cur_path = current_path + path
        if os.path.isdir(cur_path):
            current_path = cur_path
            if current_path[-1] != '/':
                current_path = current_path + '/'
            return True
        return False


dispatcher = SoapDispatcher(
    'my_dispatcher', 
    location='http://localhost:8008/', 
    action='http://localhost:8008/', 
    namespace='http://example.com/sample.wsdl', 
    prefix='ns0', 
    trace=True, 
    ns=True)

dispatcher.register_function('rm', rm, 
    returns={'Result': bool}, 
    args={'filename': str})

dispatcher.register_function('cp', cp, 
    returns={'Result': bool}, 
    args={'src': str, 'dest': str})

dispatcher.register_function('rename', rename, 
    returns={'Result': bool}, 
    args={'src': str, 'dest': str})

dispatcher.register_function('ls_dir', ls_dir, 
    returns={'Result': list}, 
    args={'path': str})

dispatcher.register_function('ls_file', ls_file, 
    returns={'Result': list}, 
    args={'path': str})

dispatcher.register_function('mkdir', mkdir, 
    returns={'Result': bool}, 
    args={'path': str})

dispatcher.register_function('rmdir', rmdir, 
    returns={'Result': bool}, 
    args={'path': str})

dispatcher.register_function('getsize', getsize, 
    returns={'Result': int}, 
    args={'filename': str})

dispatcher.register_function('sendfile', sendfile, 
    returns={'Result': int}, 
    args={'buf': str})

dispatcher.register_function('getfile', getfile, 
    returns={'Result': str}, 
    args={'filename': str,'ip':str,'port':str})

dispatcher.register_function('cd', cd, 
    returns={'Result': bool}, 
    args={'path': str})

dispatcher.register_function('pwd', pwd, 
    returns={'Result': str}, 
    args={})

if __name__ == '__main__':
    print 'Starting server...'
    #print AbsolutePath('/123.sh')
    
    path='/mnt'
    iface='192.168.16.105'
    if len(sys.argv)==2:
	iface=sys.argv[1]
    elif len(sys.argv)==3:
	iface=sys.argv[1]
	path=sys.argv[2]
    else:
	pass
    fileport=8001
    soapport=8008
    t=threading.Thread(target=fileserver.recvfile,args=(path,iface,fileport))
    t.setDaemon(True)
    t.start()
    httpd = HTTPServer(('', soapport), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()

