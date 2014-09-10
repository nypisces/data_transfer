import sys

import MySQLdb as mysql


class MysqlClient():
    def __init__(self):
        """mysql info"""
        self.dbHost = 'kanbaiyin.cqk1mut4ciue.rds.cn-north-1.amazonaws.com.cn'
        self.dbUser = 'root'
        self.dbPass = '88888888'
        self.dbName = 'kanbaiyin_default'
        self.port = 3306
#         self.dbHost = 'localhost'
#         self.dbUser = 'root'
#         self.dbPass = ''
#         self.dbName = 'kanbaiyin_default'
#         self.port = 3306
        self._conn()

    def _conn(self):
        '''mysql connect'''
        self.conn = mysql.Connection(self.dbHost, self.dbUser, self.dbPass, self.dbName, int(self.port))
        self.conn.autocommit(True)
        self.conn.select_db(self.dbName)
        self.cur = self.conn.cursor()
        self.setName()

    def setName(self):
        '''set name for utf-8'''
        self.cur.execute("SET NAMES 'utf8'")
        self.cur.execute("SET CHARACTER SET 'utf8'")

    def _close(self):
        '''close the mysql connect'''
        # self.cur.close()

    def selectQuery(self, params):
        par = ','.join(params['name'])
        sql = "select " + par + " from " + params['tbl'] + " " + params['prefix']
        self.sql = sql
        self.queryNum = self.cur.execute(sql)
        self.params = params

    def query(self, sql):
        try:
            self.queryNum = self.cur.execute(sql)
            return True
        except:
            return False

    def getSql(self):
        fetch = self.cur.fetchall()
        for inv in fetch:
            yield dict(zip(self.params['name'], inv))

    def fn(self):
        return self.cur.rowcount

    def getTableList(self, tblName):
        try:
            self.cur.execute("desc " + tblName)
            return [row[0] for row in self.cur.fetchall()]
        except:
            sys.exit(0)

    def getDbList(self):
        try:
            self.cur.execute("show tables")
            return [row[0] for row in self.cur.fetchall()]
        except:
            sys.exit(0)

    def __del__(self):
        try:
            self.__close__()
        except:
            "the connect could not close"
