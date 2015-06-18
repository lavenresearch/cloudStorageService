#!/bin/sh
homeDir=$(pwd)
cd $homeDir
./configure && make && make install
