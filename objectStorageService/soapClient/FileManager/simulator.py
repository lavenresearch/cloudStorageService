#!/usr/bin/env python
#coding=utf-8
from client import MyClient
from pysimplesoap.client import SoapClient, SoapFault
#getfile,sendfile,rm,cp,rename,ls_dir,ls_file,mkdir,rmdir,getsize,cd,server_ip,server_port
import sys
class simulator():
    def __init__(self, client):
        self.client=client
	self.command={'cd':self.client.cd,'mkdir':self.client.mkdir,'rmdir':self.client.rmdir,'ls':self.ls,'rename':self.client.rename,\
	'cp':self.client.cp,'rm':self.client.rm,'sendfile':self.client.sendfile,'getfile':self.client.getfile,'help':self.helpme}
    def helpme(self):
        print '''
         Usage:
             command cd:
                 cd path, go to a path
 
             command mkdir:
                 mkdir path, make a folder
 
             command ls:
                 ls [path], list all folders and files
             
             command rename:
                 rename srcfile destfile, rename a file
 
             command cp:
                 cp srcfile destfile, copy a file to another file
 
             command rm:
                 rm filename, remove a file
 
             command sendfile:
                 sendfile filename[,path], send a file into a path
 
             command getfile:
                 getfile filename[,path], get a file into a path
              '''
    def ls(self,path='./'):
    	file_list=self.client.ls_file(path)
     	dir_list=self.client.ls_dir(path)

     	file_list.sort()
     	dir_list.sort()

     	for name in dir_list:
            if len(name)!=0:
                if name[0]!='.':
                    sys.stdout.write('\033[34m')
                    sys.stdout.write(name+'\t')
                    sys.stdout.write('\033[0m')

        for name in file_list:
            if len(name)!=0:
            	if name[0]!='.':
                    sys.stdout.write(name+'\t')
     	sys.stdout.write('\n')
    
    def start(self):
        
	while 1:
    	    cmd=raw_input('@'+server_ip+'>>')
            cmd=cmd.strip()
    	    if cmd=='':
                continue
    	    cmd=cmd.split(' ')
    	    if cmd[0]=='exit' or cmd[0]=='quit':
        	break
     
    	    elif cmd[0] in self.command:
                #try:
        	tempcmd=tuple(cmd[1:])
        	self.command[cmd[0]](*tempcmd)
        	#except:
        	#    print 'invalid input, please try again'
    	    else:
        	print 'no such command'

if __name__=='__main__':
    #server_ip='192.168.16.101'
    #server_port='8008'
    args=sys.argv
    if len(args)==3:
        server_ip=args[1]
        server_port=args[2]
    elif len(args)==2:
        server_ip=args[1]
	server_port='8008'	
    else:
        pass

    fulladdr="http://"+server_ip+":"+server_port+"/"
    soapinfo = SoapClient(
            location = fulladdr,
        action = fulladdr, # SOAPAction
        namespace = "http://example.com/sample.wsdl",
        soap_ns='soap',
        trace = True,
        ns = False)
    my=MyClient(soapinfo)
    sim=simulator(my)
    sim.start()
