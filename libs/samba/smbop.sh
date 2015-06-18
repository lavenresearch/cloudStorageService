#!/bin/bash

_opt=$1
_user=$2
_passwd=$3
_userexpectfile=./.userexpectbin
_smbexpectfile=./.smbexpectbin
_defaultgroup=smbshare


## smb share dir path ##
_priDir=/mnt/smbUsers
_publicShare=/mnt/smbShare/publicShare
_publicEdit=/mnt/smbShare/publicEdit

add_systemuser()
{
	useradd $_user
}

create_userexpectfile()
{

cat > $_userexpectfile <<TT
#!/usr/bin/expect

spawn passwd $_user 
expect "*:"
send "$_passwd\n"
expect "*:"
send "$_passwd\n"
interact
TT 
TT

sed -i "s/TT/\ /g" $_userexpectfile

}

remove_expectfile()
{
	rm -rf $_userexpectfile $_smbexpectfile
}

create_smbexpectfile()
{

cat > $_smbexpectfile <<TAG
#!/usr/bin/expect

spawn smbpasswd -a $_user 
expect "password:"
send "$_passwd\n"
expect "password:"
send "$_passwd\n"
interact
TAG 
TAG

sed -i "s/TAG/\ /g" $_smbexpectfile

}

creat_smbshareDir(){

	mkdir -pv $_priDir
	mkdir -pv $_publicShare
	mkdir -pv $_publicEdit
	chmod 1777 $_publicEdit
}

cfg_samba(){
	mv /etc/samba/smb.conf /etc/samba/smb.conf.org
	\cp -f ./smb.conf /etc/samba/
	service smb restart
}

creat_smbgroup(){
    groupadd $_defaultgroup
}

addtosys(){
	useradd $_user
	_uid=`id $_user|awk '{print $1}'|cut -d= -f2 |cut -d\( -f1`
	usermod -d $_priDir/$_user -u $_uid $_user
	mv /home/$_user /mnt/smbUsers/
	create_userexpectfile
	/usr/bin/expect -f $_userexpectfile
	groupadd $_defaultgroup
	usermod -a -G $_defaultgroup $_user 
}

addtosmb(){
	create_smbexpectfile
	/usr/bin/expect -f $_smbexpectfile
	/etc/init.d/smb restart
}

usage(){
	echo "-------------------------------------------------------"
	echo "   pre op: yum install samba samba-client samba-swat   "
	echo "   pre op: yum install expect spawn finger             "
	echo "-------------------------------------------------------"
	echo "usage:"
	echo "   $0 --cfgsmb:  config && restart the samba server    "
	echo "   $0 --adduser username password:                     "
	echo "                         add samba user                "
	echo "   $0 --help:    operation manual                      "
	echo "-------------------------------------------------------"
}


case $_opt in
	"--help")
		usage
		;;
	"--cfgsmb")
		creat_smbshareDir
		cfg_samba
		;;
	"--adduser")
		addtosys
		addtosmb
		remove_expectfile
		;;
	*)
		usage
		;;
esac
