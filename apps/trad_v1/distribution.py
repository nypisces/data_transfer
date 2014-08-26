
import json
import time


from py_redis import RedisClient
from py_mysql import MysqlClient


class Distribution():
    def __init__(self, treaty):
        self.mysql_client = MysqlClient()
        self.treaty = treaty

    def get_data(self):
        self.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        t = time.localtime(time.time() - 15 * 60)
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
        self.opening = self.get_opening()
        (self.sellone, self.last_time) = self.get_sellone()
        (self.highest, self.lowest) = self.get_high_low()
        (self.lastsettle, self.closed) = self.get_close()
        self.table_name = self.get_tablename(self.treaty)
        self.data_list = self.data_to_list()
        self.insert_db()

    def get_opening(self):
        params = {'name': ['sellone'],
                  'tbl': 'trade_data',
                  'prefix': ' where treaty="{2}" and selltime between "{0}" and "{1}" order by id asc limit 1'.format(self.start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return item['sellone']
        return 0

    def get_sellone(self):
        params = {'name': ['sellone', 'selltime'],
                  'tbl': 'trade_data',
                  'prefix': ' where treaty="{2}" and selltime between "{0}" and "{1}" order by id desc limit 1'.format(self.start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['sellone'], item['selltime'])
        return (0, 0)

    def get_close(self):
        params = {'name': ['lastsettle', 'closed'],
                  'tbl': 'trade_data',
                  'prefix': ' where treaty="{2}" and selltime between "{0}" and "{1}" limit 1'.format(self.start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['lastsettle'], item['closed'])
        return (0, 0)

    def get_high_low(self):
        params = {'name': ['max(sellone)', 'min(sellone)'],
                  'tbl': 'trade_data',
                  'prefix': ' where treaty="{2}" and selltime between "{0}" and "{1}"'.format(self.start_time, self.end_time, self.treaty)}
        self.mysql_client.selectQuery(params)
        query = self.mysql_client.getSql()
        for item in query:
            return (item['max(sellone)'], item['min(sellone)'])
        return (0, 0)

    def get_tablename(self, treaty):
        table_dict = {
            'XAGUSD': 'trade_xagusd',
            'PD': 'trade_pd',
            'PT': 'trade_pt',
            'NI': 'trade_ni',
            'CU': 'trade_cu',
            'AL': 'trade_al',
            'AUT+D': 'trade_aut',
            'AGT+D': 'trade_agt',
            'AU9999': 'trade_au99',
            'AU9995': 'trade_au95',
            'CUAU100G': 'trade_cuau',
            'MAUT+D': 'trade_maut'
        }
        return table_dict.get(treaty)

    def insert_db(self):
        sql = 'insert into {0} (treaty, opening, highest, lowest, sellone, lastsettle, closed, add_time, treaty_data) values \
                ("{1}",{2},{3},{4},{5},{6},{7},"{8}","{9}")'.format(self.table_name,
                                                                    self.treaty,
                                                                    self.opening,
                                                                    self.highest,
                                                                    self.lowest,
                                                                    self.sellone,
                                                                    self.lastsettle,
                                                                    self.closed,
                                                                    self.end_time,
                                                                    str(self.data_list)) 
        self.mysql_client.query(sql)

    def get_treaty_data(self):
        self.treaty_data = {'treaty': self.treaty,
                            'opening': self.opening,
                            'highest': self.highest,
                            'lowest': self.lowest,
                            'sellone': self.sellone,
                            'lastsettle': self.lastsettle,
                            'closed': self.closed,
                            'add_time': str(self.last_time)}
        return self.treaty_data

    def data_to_list(self):
        self.data_list = [self.opening, self.closed, self.sellone, self.highest, self.lowest]
        return self.data_list

if __name__ == '__main__':
    treaty_list = ['XAGUSD', 'PD', 'PT', 'NI', 'CU', 'AL', 'AUT+D', 'AGT+D', 'AU9999', 'AU9995', 'CUAU100G', 'MAUT+D']
    treaty_data_list = []
    redis_client = RedisClient()
    for treaty in treaty_list: 
        distribution = Distribution(treaty)
        distribution.get_data()
        treaty_data = distribution.get_treaty_data()
        treaty_data_list.append(treaty_data)
    redis_client.saveValue('treaty_data', json.dumps(treaty_data_list))