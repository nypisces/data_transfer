import json
import traceback

from redis import Redis

from py_mysql import MysqlClient


redis = Redis(host='54.223.140.206', port=6379, db=0)


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
    sql = 'insert into products_data (symbol, sellone, selltime, last_sett, last_close) \
        values \
        ("{}",{},"{}",{},{})'.format(str(res[0]), res[9], str(trade_time), res[-2], res[-1])
    return sql


def write_into_redis(data):
    data_list = [data[4], data[5], data[6], data[9], data[-2], data[-1]]
    redis_key = data[0]
    redis.set(redis_key, json.dumps(data_list))

if __name__ == '__main__':     
    while True:
        try:
            res = redis.rpop('sg.market')
            result = redis.rpop('tg.market')
            if res is not None:
                res = res.decode('gb2312').split(',')
                trade_time = trans_redis(res)
                mysql_client = MysqlClient()
                insert_sql = get_sql(res)
                mysql_client.query(insert_sql)
                write_into_redis(res)
            if result is not None:
                result = result.decode('gb2312').split(',')
                trade_time = trans_redis(result)
                mysql_client = MysqlClient()
                insert_sql = get_sql(result)
                mysql_client.query(insert_sql)
                write_into_redis(res)
        except:
            traceback.print_exc(5)
