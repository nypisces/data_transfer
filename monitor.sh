#!/bin/bash

redis_process=$(ps -ef | grep "redis_server.py" | grep -v grep)
sms_process= $(ps -ef|grep "send_sms.py" | grep -v grep)

echo "redis_process ======${redis_process}"
echo "sms_process======${sms_process}"
if [[ "x${redis_process}" == "x" ]]
then
	nohup /usr/bin/python3 /home/ubuntu/GitHub/data_transfer/apps/products/redis_server.py 1>&2 >>/dev/null &
fi

if [[ "x"${sms_process} == "x" ]]
then
	nohup /usr/bin/python3 /home/ubuntu/GitHub/data_transfer/apps/products/send_sms.py 1>&2 >>/dev/null &
fi
