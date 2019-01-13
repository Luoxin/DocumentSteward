'''
和sqlite数据库连接相关的类
'''
import traceback
import sys
import os

from get_file_attributes import *

import hashlib

import sqlite3

class DBSqlite:
    def __init__(self, db_path="DocumentSteward.db"):
        self.db_path = db_path

        self.delete_sql = "delete from 'file_directory_table' where 'status' = -1"


        if not os.path.exists(self.db_path):
            self.initialize_the_database()

    def initialize_the_database(self):
        if not os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except:
                pass
            create_sql = '''
                 CREATE TABLE \"file_directory_table\"
                (
                    file_name text,
                    absolute_path text not null constraint file_directory_table_pk primary key,
                    file_id text,
                    file_create_time int,
                    file_modify_time int,
                    file_size text,
                    file_type text,
                    status int default 0
                )
            '''

            status, result = self.execute_by_sql(create_sql)
            print(result)

        # TODO:创建表

    def initial_file_index(self, file_list):  # 初始化文件索引
        count = 0
        value_str = ""
        for index, file_message in enumerate(file_list):
            try:
                count += 1
                value_str += "('{}', '{}', '{}', '{}', '{}', '{}', '{}'),".format(file_message['file_name'],
                                                                                      file_message['absolute_path'],
                                                                                      hashlib.md5(file_message['absolute_path'].encode('utf-8')).hexdigest(),
                                                                                      file_message["file_create_time"],
                                                                                      file_message["file_modify_time"],
                                                                                      str(file_message["file_size"][0]) + file_message["file_size"][1],
                                                                                      file_message["file_type"],)
            except:
                if file_message is None:
                    pass
                else:
                    traceback.print_exc()

        insert_sql = "REPLACE INTO 'file_directory_table'('file_name', 'absolute_path', 'file_id', 'file_create_time', 'file_modify_time', 'file_size', 'file_type') VALUES {}".format(value_str[:-1])
        status, result = self.execute_by_sql(insert_sql)
        # if status != True:
        #     print(insert_sql)
        del insert_sql, value_str
        return status

    def clean_up_redundant_data(self):
        status, result = self.execute_by_sql(self.delete_sql)
        # print(status, result)

    def set_database_path(self, db_path):  # 设置数据库路径
        try:
            self.db_path = db_path
        except:
            traceback.print_exc()

    def execute_by_sql(self, *args): # 根据标准输入对数据库操作
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if args.__len__() == 2:
                result = cursor.execute(args[0], args[1])
                result = result.fetchall()
                if result.__len__() == 0:
                    result = (True, tuple())
                else:
                    result = (True, tuple(result))
            elif args.__len__() == 1:
                result = cursor.execute(args[0])
                result = result.fetchall()
                if result.__len__() == 0:
                    result = (True, tuple())
                else:
                    result = (True, result)
            else:
                result = (False, "Incoming parameter type error")
            conn.commit()
            cursor.close()
            conn.close()
            result = result
        except :
            result = (False, traceback.format_exc())
        finally:
            return result

    def insert_by_value(self, table, fields, values):  # 根据值插入数据
        '''
        根据值插入数据
        :param table: 表名(string)
               fields: 字段名(list/tuple)
               values: 值名称(list/tuple)
        :return:
        '''
        try:
            if ((isinstance(fields, list) or isinstance(fields, tuple))
                    and (isinstance(values, list) or isinstance(values, tuple))
                    and isinstance(table, str)
                    and fields.__len__() is values.__len__()):
                insert_sql = 'insert into "{}" ({}) values ({})'.format(table, ",".join([f"'{i}'" for i in fields]), "?,".join(["" for i in range(fields.__len__())])[:-1])
                pare = tuple(values)
                result = self.execute_by_sql(insert_sql, pare)
            else:
                result = (False, "Incoming parameter type error")
        except:
            # traceback.print_exc()
            result = (False, traceback.format_exc())
        finally:
            return result

    def select_by_value(self, table, fields, requirement=None):  # 根据字段获取值
        '''
        根据字段获取值
        :param table: 表名(string)
               fields: 字段名(*/tuple/list)
               requirement: 查询条件(string/None)
        :return:
        '''
        try:

            if ((isinstance(fields, list) or isinstance(fields, tuple))  # 有字段名
                    and isinstance(table, str)
                    and (isinstance(requirement, str) or requirement is None)):  # 输入了字段
                select_sql = "select {} from {}".format(",".join([i for i in fields]), table)

                if requirement is not None:
                    select_sql += "  where  {}".format(requirement)
                status, result = self.execute_by_sql(select_sql)
                if status:
                    if result.__len__() is 0:
                        result = (True, tuple())
                    else:
                        result = self.tuple_to_dict(fields, result)
                        result = (True, result)
                else:  # 状态是错误
                    result = (False, "Incoming parameter type error")
                pass

            elif (fields == "*"  # 没有字段名
                  and isinstance(table, str)):  # 输入了*
                get_fileds_name_sql = "PRAGMA table_info('{}')".format(table)  # 获取字段

                status, result = self.execute_by_sql(get_fileds_name_sql)
                if status:
                    fields = [i[1] for i in result]
                    result = self.select_by_value(table, fields, requirement)  # 根据字段名回调本身获取数据
                else:
                    result = (False, "Unable to get field name")
                pass
            else:
                result = (False, "Incoming parameter type error")
        except:
            # traceback.print_exc()
            result = (False, traceback.format_exc())
        finally:
            return result

    def select_by_sql(self, sql):  # 根据sql获取值
        try:
            if isinstance(sql, str):

                # 解析where条件
                temp = sql.split("WHERE")
                if temp.__len__() is 1:
                    temp = temp[0].split("where")
                if temp.__len__() is 1:
                    requirement = None
                else:
                    requirement = temp[1]
                # 解析from表
                temp = temp[0].split("FROM")
                if temp.__len__() == 1:
                    temp = temp[0].split("from")
                table = temp[1].replace(" ", "").replace("`", "").replace("\"", "").replace("'","")

                # 解析select
                temp = temp[0].split("SELECT")
                if temp.__len__() == 1:
                    temp = temp[0].split("select")
                fields = temp[1].replace(" ", "")
                if fields == '*':
                    pass
                else:
                    fields = fields.split(",")
                result = self.select_by_value(table, fields, requirement)
            else:
                result = (False, "Incoming parameter type error")
        except:
            result = (False, traceback.format_exc())
        finally:
            return result

    def tuple_to_dict(self, fields, data):  # 将得到的数据格式化
        result = []
        for data_one in data:
            result.append(dict(zip(fields, data_one)))
        return tuple(result)

if __name__ == '__main__':
    DBSqlite()