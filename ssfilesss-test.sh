#!/bin/bash

#curl -X POST -H "Content-Type: application/json" -d '{"file": "/home/garry/work/ssfiless/requirements.txt"}' http://10.0.2.15:8080/upload

echo POST
oo=`curl -s -X POST -H "Content-Type: application/json" -d '{"file": "requirements.txt"}' http://10.0.2.15:8080/upload`
echo $oo
echo

echo GET
curl -s -X GET -H "Content-Type: application/json" $oo
echo
