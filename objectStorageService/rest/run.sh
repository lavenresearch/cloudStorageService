#!/bin/sh
path=$(dirname $(which $0))
echo $path
# python $path/mock-s3/setup.py install
ip=`ifconfig | grep inet\ addr:192.168 | awk '{print $2}' | cut -d ":"  -f 2`
mock_s3 --hostname $ip --root=/mnt/s3store
