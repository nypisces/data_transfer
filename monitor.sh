#!/bin/bash
##用来监控python的进程是否存在

redis_process=$(ps -ef | grep "redis_server.py" | grep -v grep)
sms_process= $(ps -ef|grep "send_sms.py" | grep -v grep)

if [[ "x${redis_process}" == "x"]]
then
	nohup /usr/bin/python3 /home/ubuntu/GitHub/data_transfer/apps/products/redis_server.py >/dev/null &
fi

if [[ "x"${sms_process} == "x" ]]
then
	nohup /usr/bin/python3 /home/ubuntu/GitHub/data_transfer/apps/products/send_sms.py >/dev/null &
fi
