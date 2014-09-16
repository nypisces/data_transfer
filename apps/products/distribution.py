import time
import traceback

from py_mysql import MysqlClient
from py_redis import RedisClient


class Distribution():
    def __init__(self, treaty):
        self.mysql_client = MysqlClient()
        self.treaty = treaty

    def get_data(self):
        self.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # self.quote_datetime = self.datetime_to_int(self.end_time)
        cur_min = int(time.localtime(time.time()).tm_min)
        if int(cur_min) == 0:
            t = time.localtime(time.time() - 60 * 60)
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
            interval = '1h'
            quote_datetime = self.datetime_to_int(start_time)
            self.get_result(start_time, quote_datetime, interval)
        t = time.localtime(time.time() - 15 * 60)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
        interval = '15'
        quote_datetime = self.datetime_to_int(start_time)
        self.get_result(start_time, quote_datetime, interval)

    def get_result(self, start_time, quote_datetime, interval):
        self.open = self.get_opening(start_time)
        (self.close, self.last_time) = self.get_sellone(start_time)
        (self.high, self.low) = self.get_high_low(start_time)
        (self.last_sett, self.last_close) = self.get_close(start_time)
        self.table_name = 'quote_data'
        self.insert_db(quote_datetime, interval)

    def get_opening(self, start_time):
        params = {'name': ['sell_one'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and sell_time between "{0}" and "{1}" order by id asc limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return item['sell_one']
        return 0

    def get_sellone(self, start_time):
        params = {'name': ['sell_one', 'sell_time'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and sell_time between "{0}" and "{1}" order by id desc limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['sell_one'], item['sell_time'])
        return (0, 0)

    def get_close(self, start_time):
        params = {'name': ['last_sett', 'last_close'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and sell_time between "{0}" and "{1}" limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['last_sett'], item['last_close'])
        return (0, 0)

    def get_high_low(self, start_time):
        params = {'name': ['max(sell_one)', 'min(sell_one)'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and sell_time between "{0}" and "{1}"'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['max(sell_one)'], item['min(sell_one)'])
        return (0, 0)

    def insert_db(self, start_time, interval):
        sql = 'insert into {0} (`symbol`, `open`, `high`, `low`, `close`, `last_sett`, `last_close`, `time_stamp`,`time_frame`) values \
                ("{1}",{2},{3},{4},{5},{6},{7},{8},"{9}")'.format(self.table_name,
                                                                  self.treaty,
                                                                  self.open,
                                                                  self.high,
                                                                  self.low,
                                                                  self.close,
                                                                  self.last_sett,
                                                                  self.last_close,
                                                                  int(start_time),
                                                                  interval) 
        self.mysql_client.query(sql)

    def datetime_to_int(self, datetime):
        timeArray = time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(timeArray))


if __name__ == '__main__':
    treaty_list = ['XAGUSD', 'PD', 'PT', 'NI', 'CU', 'AL', 'AUT+D', 'AGT+D', 'AU9999', 'AU9995', 'AU100G', 'MAUT+D']
    treaty_data_list = []
    redis_client = RedisClient()
    for treaty in treaty_list:
        try: 
            distribution = Distribution(treaty)
            distribution.get_data()
        except:
            traceback.print_exc(5)
            pass