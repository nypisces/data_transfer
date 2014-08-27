
import json
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
        self.quate_datetime = self.datetime_to_int(self.end_time)
        cur_min = int(time.localtime(time.time()).tm_min)
        if cur_min == 0:
            t = time.localtime(time.time() - 60 * 60)
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
            interval = 60
            self.get_result(start_time, interval)
        t = time.localtime(time.time() - 15 * 60)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
        interval = 15
        self.get_result(start_time, interval)

    def get_result(self, start_time, interval):
        self.open = self.get_opening(start_time)
        (self.close, self.last_time) = self.get_sellone(start_time)
        (self.high, self.low) = self.get_high_low(start_time)
        (self.last_sett, self.last_close) = self.get_close(start_time)
        self.table_name = 'quate_data'
        self.insert_db(interval)

    def get_opening(self, start_time):
        params = {'name': ['sellone'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and selltime between "{0}" and "{1}" order by id asc limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return item['sellone']
        return 0

    def get_sellone(self, start_time):
        params = {'name': ['sellone', 'selltime'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and selltime between "{0}" and "{1}" order by id desc limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['sellone'], item['selltime'])
        return (0, 0)

    def get_close(self, start_time):
        params = {'name': ['last_sett', 'last_close'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and selltime between "{0}" and "{1}" limit 1'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['last_sett'], item['last_close'])
        return (0, 0)

    def get_high_low(self, start_time):
        params = {'name': ['max(sellone)', 'min(sellone)'],
                  'tbl': 'products_data',
                  'prefix': ' where symbol="{2}" and selltime between "{0}" and "{1}"'.format(start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['max(sellone)'], item['min(sellone)'])
        return (0, 0)

    def insert_db(self, interval):
        sql = 'insert into {0} (`symbol`, `open`, `high`, `low`, `close`, `last_sett`, `last_close`, `quate_datetime`,`interval`) values \
                ("{1}",{2},{3},{4},{5},{6},{7},{8},{9})'.format(self.table_name,
                                                                self.treaty,
                                                                self.open,
                                                                self.high,
                                                                self.low,
                                                                self.close,
                                                                self.last_sett,
                                                                self.last_close,
                                                                int(self.quate_datetime),
                                                                int(interval)) 
        print(sql)
        self.mysql_client.query(sql)

    def datetime_to_int(self, datetime):
        timeArray = time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(timeArray))


if __name__ == '__main__':
    treaty_list = ['XAGUSD', 'PD', 'PT', 'NI', 'CU', 'AL', 'AUT+D', 'AGT+D', 'AU9999', 'AU9995', 'CUAU100G', 'MAUT+D']
    treaty_data_list = []
    redis_client = RedisClient()
    for treaty in treaty_list:
        try: 
            distribution = Distribution(treaty)
            distribution.get_data()
        except:
            #traceback.print_exc(5)
            pass