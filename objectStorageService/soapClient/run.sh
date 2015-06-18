#!/bin/sh
path=$(dirname $(which $0))
echo $path
cd $path/FileManager
python simulator.py {$1}
#rm -rf build
#rm -rf dist
#rm -rf mock_s3.egg-info
