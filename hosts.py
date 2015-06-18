import os
import sys
import socket

def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False

def get_all_hostname_dirs(path):
    all_items=os.listdir(path)
    dirs=[]
    for item in all_items:
	fullpath=os.path.join(path,item)
        if os.path.isdir(fullpath) and os.path.getsize(fullpath)==4096 \
		and not valid_ip(item):
            dirs.append(item)
    return dirs

def get_all_clients_ip(hosts='/etc/hosts',rrds_path='/var/lib/ganglia/rrds/client/'):
    fp=open(hosts,'r')
    result01=[]
    while True:
        line=fp.readline()
        if not line: break
        result01.append(line.strip())
    #print result01

    result02=[]
    for i in range(0,len(result01)):
        if result01[i]!='':
	    if result01[i][0]!='#':
	        result02.append(result01[i])
    for i in range(0,len(result02)):
        result02[i]=result02[i].split(' ')
    #print result02

    result03=[]
    for i in range(0,len(result02)):
        if valid_ip(result02[i][0]):
	    result03.append(result02[i])
    #print result03

    for i in range(0,len(result03)):
	temp=[]
	for j in range(0,len(result03[i])):
	    if result03[i][j]!='':
		temp.append(result03[i][j])
	result03[i]=temp
    #print result03
    dirs=get_all_hostname_dirs(rrds_path)
    
    ips=[]
    for k in range(0,len(dirs)):
	for i in range(0,len(result03)):
	    get=0
	    for j in range(1,len(result03[i])):
		if dirs[k]==result03[i][j]:
		    get=1
	    	    ips.append(result03[i][0]) #add ip to list ips
		    break	    
	    if get==1:
		break
    fp.close()
    return ips

if __name__=='__main__':
    ips=get_all_clients_ip('/etc/hosts','./client/')	
    print ips
