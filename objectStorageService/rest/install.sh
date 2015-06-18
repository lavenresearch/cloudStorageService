#!/bin/sh
path=$(dirname $(which $0))
echo $path
cd $path/mock-s3
python setup.py install
#rm -rf build
#rm -rf dist
#rm -rf mock_s3.egg-info
