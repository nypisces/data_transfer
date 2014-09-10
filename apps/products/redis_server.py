import json
import time
import traceback

from redis import Redis

from py_mysql import MysqlClient


redis = Redis(host='54.223.140.206', port=6379, db=0)


def close_monitor(query):

    for data in query:
        create_time = data['created']
        period = int(data['period'])
        pass_time = int_to_datetime(int(time.time()) - period * 60 * 60)
        if pass_time > create_time:
            delete_sms_order(query)
        else:
            pass
    cur_day = time.localtime(int(time.time())).tm_mday
    cur_hour = time.localtime(int(time.time())).tm_hour
    cur_min = time.localtime(int(time.time())).tm_min
    if cur_day == 1 and cur_hour == 0 and cur_min == 1:
        sql = 'delete from sms_order where xpired_flag =1'
        mysql_client.query(sql)


def int_to_datetime(timeStamp):
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def trans_redis(data):
    date_strs = data[2]
    trans_date = '{}-{}-{}'.format(date_strs[0:4], date_strs[4:6], date_strs[6:])
    time_str = data[3]
    if len(time_str) < 7:
        num = 7 - len(time_str)
        time_str = '0' * num + time_str
    trans_time = '{}:{}:{}'.format(time_str[0:2], time_str[2:4], calc_second(time_str[4:]))
    return '{} {}'.format(trans_date, trans_time)


def calc_second(sed):
    try:
        second = int(sed) // 10
        if second < 10:
            second = '0{}'.format(second)
        return second
    except:
        return '00'


def get_sql(res):
    sql = 'insert into products_data (symbol, sell_one, sell_time, last_sett, last_close) \
        values \
        ("{}",{},"{}",{},{})'.format(str(res[0]), res[9], str(trade_time), res[-2], res[-1])
    return sql


def write_into_redis(data, trade_time):
    """
数据的顺序：产品类型，开盘价，最高价，最低价，卖一价，昨结，昨收
    """
    # print('----------{}'.format(data))
    # print(trade_time)
    data_list = [data[0], trade_time, float(data[4]), float(data[5]), float(data[6]), float(data[9]), int(data[-2]), float(data[-1])]
    redis_key = data[0]
    redis.set(redis_key, json.dumps(data_list))


def sms_into_redis(query):
    redis_key = 'sms'
    redis.lpush(redis_key, json.dumps(query))


def Compare(res, query):
    for item in query:
        if str(res[0]) == str(item['treaty']):
            if int(item['direction']) == 1:
                if float(res[9]) > float(item['price']):
                    item['sellone'] = float(res[9])
                    sms_into_redis(item)
                    delete_sms_order(item)
            elif int(item['direction']) == 2:
                if float(res[9]) < float(item['price']):
                    item['sellone'] = float(res[9])
                    sms_into_redis(item)
                    delete_sms_order(item)


def delete_sms_order(query):
    sql = 'update sms_order set xpired_flag=1 where id = {}'.format(query['id'])
    mysql_client.query(sql)


def datetime_to_int(self, datetime):
    timeArray = time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray))


if __name__ == '__main__':
    mysql_client = MysqlClient()     
    while True:
        try:
            params = {
                'name': ['id', 'direction', 'mobile', 'name', 'treaty', 'price', 'created'],
                'tbl': 'sms_order',
                'prefix': 'where xpired_flag=0'
            }
            mysql_client.selectQuery(params)
            query = mysql_client.getSql()
            res = redis.rpop('sg.market')
            result = redis.rpop('tg.market')
            if res is not None:
                res = res.decode('gb2312').split(',')
                trade_time = trans_redis(res)
                insert_sql = get_sql(res)
                mysql_client.query(insert_sql)
                write_into_redis(res, trade_time)
                Compare(res, query)
            if result is not None:
                result = result.decode('gb2312').split(',')
                trade_time = trans_redis(result)
                insert_sql = get_sql(result)
                mysql_client.query(insert_sql)
                write_into_redis(result, trade_time)
                Compare(result, query)
            else:
                pass
            close_monitor(query)
        except:
            traceback.print_exc(5)
