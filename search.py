'''

'''
import traceback

import sys
import os

import psutil

from linkSqlite import DBSqlite

def find_procs_by_name(name):
    "Return a list of processes matching 'name'."
    ls = []
    for p in psutil.process_iter(attrs=['name']):
        if p.info['name'] == name:
            ls.append(p)
    return ls

class Search:
    def __init__(self):
        self.db = DBSqlite()

    def get_data(self, keywords):
        select_sql = 'select * from "file_directory_table" where "file_name" like "%{}%"'.format(keywords)
        # print(select_sql)
        status, result = self.db.select_by_sql(select_sql)
        if status:
            if result.__len__() != 0:
                for data in result:
                    print(data)
            print("Can't find file")
        else:
            print("Error   ", result)

if __name__ == '__main__':
    s = Search()

    ls = find_procs_by_name("File_monitoring.exe")
    if ls.__len__() != 2:  # 如果不存在其他正在执行的文件索引服务，则执行，否则退出
        os.system("start File_monitoring.exe")

    if sys.argv.__len__() == 2:
        s.get_data(str(sys.argv[1]))

    while True:
        print("请输出要查找的关键字")
        keywords = str(input())
        s.get_data(keywords)
