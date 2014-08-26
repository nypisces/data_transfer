from redis import Redis

from py_mysql import MysqlClient


redis = Redis(host='54.223.140.206', port=6379, db=0)


def trans_redis(data):
    date_strs = data[2]
    trans_date = '{}-{}-{}'.format(date_strs[0:4], date_strs[4:6], date_strs[6:])
    time_str = data[3]
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
    sql = 'insert into trade_data (treaty,sellone,selltime,lastsettle,closed) \
        values \
        ("{}",{},"{}",{},{})'.format(str(res[0]), res[9], str(trade_time), res[-2], res[-1])
    return sql


if __name__ == '__main__':     
    while True:
        res = redis.rpop('sg.market')
        result = redis.rpop('tg.market')
        if res is not None:
            res = res.decode('gb2312').split(',')
            trade_time = trans_redis(res)
            mysql_client = MysqlClient()
            insert_sql = get_sql(res)
            mysql_client.query(insert_sql)
        if result is not None:
            result = result.decode('gb2312').split(',')
            trade_time = trans_redis(result)
            mysql_client = MysqlClient()
            insert_sql = get_sql(result)
            mysql_client.query(insert_sql)
