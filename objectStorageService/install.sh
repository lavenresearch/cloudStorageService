#!/bin/sh
if [[ "$#" != 1 ]]; then
    echo "install.sh rest|soap"
else
    chmod +x ./${1}/install.sh
    ./${1}/install.sh
fi   
