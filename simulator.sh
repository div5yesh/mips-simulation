#!/bin/sh

pyt3=`which python3`
pyt=`which python`

if [ "$#" -ne 5 ]; then
    echo "Usage: simulator inst.txt data.txt reg.txt config.txt result.txt"
else
    if [ "$pyt3" != "" ]; then
        $pyt3 simulator.py $1 $2 $3 $4 $5
    elif [ "$pyt" != "" ]; then
        $pyt simulator.py $1 $2 $3 $4 $5
    else
        echo "python3/python not found."
    fi
fi