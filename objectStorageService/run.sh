#!/bin/sh
if [[ "$#" != 1 ]]; then
    echo "run.sh rest|soap"
else
    chmod +x ./${1}/run.sh
    ./${1}/run.sh
fi   
