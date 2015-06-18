#!/bin/sh
homeDir=$(pwd)
yum install mongo-10gen mongo-10gen-server
cd $homeDir/setuptools
python ez_setup.py
cd $homeDir/pymongo-3.0.2
python setup.py install
