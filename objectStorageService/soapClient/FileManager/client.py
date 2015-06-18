#coding=utf-8
from pysimplesoap.client import SoapClient, SoapFault
import pprint
import os
import os.path
import sys
import fileserver
import simplefileserver
import threading
import hashlib

class MyClient():
    def __init__(self, client):
        self.client=client
    def file_md5(self, filename):
        _FILE_SLIM = (5*1024*1024) # 5MB
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
        
    def getfile(self, filename,port='8002',path='./',iface='eth0',*args):
        fileport=int(port)
        t=threading.Thread(target=simplefileserver.recvfile,args=(path,iface,fileport))
        t.setDaemon(True)
        t.start()
        myip=simplefileserver.get_ip_address(iface)
        response = self.client.getfile(filename=filename,ip=myip,port=fileport)
        result = str(response.Result)
        md5path=os.path.join(path,os.path.basename(filename))
        t.join()
        
        hmd5=self.file_md5(md5path)
        hmd5=hmd5[0]
        print str(hmd5) 
        if str(hmd5)==result:
            return True
        else:
            return False
        
    def sendfile(self, filename,savepath,ip,port='8001',*args):
        port=int(port)
    
        simplefileserver.sendfile(filename,savepath,ip,port)
    
    def rm(self, filename,*args):
        response=self.client.rm(filename=filename)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def cp(self, src,dest,*args):
        response=self.client.cp(src=src,dest=dest)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def rename(self, src,dest,*args):
        response=self.client.rename(src=src,dest=dest)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def ls_dir(self, path,*args):
        response=self.client.ls_dir(path=path)
        dirlist=[]
        result=response.Result
        for item in result:
            dirlist.append(str(item))
    
        return dirlist
    
    def ls_file(self, path,*args):
        response=self.client.ls_file(path=path)
        filelist=[]
        result=response.Result
        for item in result:
            filelist.append(str(item))
    
        return filelist
    
    def mkdir(self, path,*args):
        response=self.client.mkdir(path=path)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def rmdir(self, path,*args):
        response=self.client.rmdir(path=path)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def getsize(self, filename,*args):
        response=self.client.getsize(filename=filename)
    
        return int(response.Result)
    
    def cd(self, path,*args):
        response=self.client.cd(path=path)
        if str(response.Result)=='true':
            return True
        else:
            return False
    
    def pwd(self):
       response =self.client.pwd()
       #print type(response.Result)
       return str(response.Result)

if __name__=='__main__':
    args=('/home/allen_lee/Dc98.gz',)
    arg=('/home/allen_lee/te.sh',)
    
    server_ip='115.156.209.190'
    server_port='8008'
    fulladdr="http://"+server_ip+":"+server_port+"/"
    client = SoapClient(
            location = fulladdr,
        action = fulladdr, # SOAPAction
        namespace = "http://example.com/sample.wsdl", 
        soap_ns='soap',
        trace = True,
        ns = False)
    my=MyClient(client)
    print my.pwd()
    #print my.getsize(*args)
    #my.getfile(*args)
    #print sendfile('/home/allen/Downloads/wps.deb','/home/allen_lee/wp.deb','115.156.209.190',8001)
