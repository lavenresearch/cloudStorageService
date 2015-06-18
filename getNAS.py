import subprocess
import sys
import redis
import hosts,suyiselect

class NASService():
    hostIP = ""
    userName = ""
    password = ""
    homeDir = ""
    port = 50000
    mountPort = 50000
    nfsDir = ""
    redisClient = None
    def __init__(self, ip, uname, password, homedir, redisIP, redisPort):
        self.hostIP = hostIP
        self.userName = uname
        self.password = password
        self.homeDir = homedir
        self.redisClient = redis.StrictRedis(host=redisIP,port=redisPort,db=0)
        curPort = self.redisClient.get("getNAScurPort")
        if curPort == None:
            curPort = 50000
        curPort = int(curPort) + 1
        self.redisClient.set("getNAScurPort",curPort)
        self.port = curPort
        self.mountPort = curPort
        self.nfsDir = "/home/oooo/nfsDirs/%s/%s" % (self.userName,self.homeDir)
    def executeRemoteCmd(self, cmd ):
        rcmd = "ssh -t root@"+self.hostIP+" \""+cmd+"\""
        print rcmd
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        p.wait()
        output = p.stdout.read()
        print output
        return output
    def exportNFS(self):
        mkdirCmd = "mkdir -p "+self.nfsDir
        self.executeRemoteCmd(mkdirCmd)
        exportsContent = "\"%s (rw,no_squash,anonuid=0,anongid=0,password=%s)\""%(self.nfsDir,self.password)
        exportsDir = "/home/oooo/exports/"
        mkdirCmd = "mkdir -p "+exportsDir
        exportsName = self.userName+self.homeDir+"exports"
        self.executeRemoteCmd(mkdirCmd)
        genExportsCmd = "echo %s > %s"%(exportsContent,exportsDir+exportsName)
        self.executeRemoteCmd(genExportsCmd)
        startNfsdCmd = "unfsd -n %d -m %d -e %s"%(self.port,self.mountPort,exportsDir+exportsName)
        self.executeRemoteCmd(startNfsdCmd)
    def printMountCmd(self):
        print "%s@%d@%s@%s"%(self.hostIP,self.port,self.password,self.nfsDir)
        print "%s#%s#"%(self.userName,self.homeDir)+"mount -o port=%d,mountport=%d,mountvers=3,nfsvers=3,nolock,tcp %s:@password:%s%s YourMountDir"%(self.port,self.mountPort,self.hostIP,self.password,self.nfsDir)+"#success"
    def exportSamba(self):
        startSambaCmd = "/root/samba/smbop.sh --adduser %s %s"%(self.userName, self.password)
        self.executeRemoteCmd(startSambaCmd)
    def printSambaInfo(self):
        print "%s#%s#%s#success"%(self.userName,self.password,self.hostIP)

        
if __name__ == '__main__':
    print "python getNAS.py userName password homeDir nasType"
    redisIP = "192.168.12.100"
    redisPort = 6379
    hIP = suyiselect.select(hosts.get_all_clients_ip())
    print hIP
    # sys.exit(0)
    hostIP = "192.168.16.102"
    userName = sys.argv[1]
    password = sys.argv[2]
    if len(sys.argv) == 4:
        nasType = sys.argv[3]
    else:
        homeDir = sys.argv[3]
        nasType = sys.argv[4]
    if nasType == 'nfs':
        nfsS = NASService(hostIP,userName, password, homeDir, redisIP, redisPort)
        nfsS.exportNFS()
        nfsS.printMountCmd()
    else:
        sambaS = NASService(hostIP,userName, password, userName, redisIP, redisPort)
        sambaS.exportSamba()
        sambaS.printSambaInfo()
    
