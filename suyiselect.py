#!/usr/bin/env python
import sys
import os
import random
import socket
import hosts

'''def valid_ip(address):
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
    return ips
'''

def select(ips):
    rand_number=random.randint(0,len(ips)-1)
    return ips[rand_number]
    
if __name__=='__main__' :
    ips=[]
    path='./client/'
    if len(sys.argv)==2:
        path=sys.argv[1]
        ips=hosts.get_all_clients_ip(rrds_path=path)
    elif len(sys.argv)==1:
        ips=hosts.get_all_clients_ip()
    else:
        print ips
    if len(ips)!=0:
        selected=select(ips)
        print selected
