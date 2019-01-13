# 监控文件的增加删除
import hashlib
import traceback

from watchdog.observers import Observer
from watchdog.events import *

import time

from get_file_attributes import *

from linkSqlite import DBSqlite

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.db = DBSqlite()
        self.updata_sql = "replace into 'file_directory_table' (absolute_path, status) values ('{}',-1)"


    def on_moved(self, event):  # 文件移动
        print(self.db.execute_by_sql(self.updata_sql.format(str(event.src_path).replace("\\", "/").replace("\\\\", "/").replace("'", "\\\'").replace("\"", "\\\""))))  # 删除旧的
        self.get_file_attributes_all(event.dest_path)  # 更新新的


        # if event.is_directory:
        #     print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        # else:
        #     print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def get_file_attributes_all(self, path):  # 获取文件的完整属性
        try:
            path = path.replace("\\", "/").replace("\\\\", "/").replace("'", "\\\'").replace("\"", "\\\"")
            # file = file.replace("'", "\\\'").replace("\"", "\\\"")
            file_message = {}
            file_message["file_name"] = os.path.split(path)[1]  # 文件名
            file_message["absolute_path"] = path  # 绝对路径
            file_message["file_modify_time"] = int(time.time())  # 修改时间
            file_message["file_size"] = get_FileSize(file_message["absolute_path"])  # 文件大小
            try:  # 文件属性
                file_message["file_type"] = os.path.splitext(file_message["file_name"])[1][1:]
            except:
                file_message["file_type"] = None

            file_message["file_create_time"] = file_message["file_modify_time"]
            try:
                hash_str = hashlib.md5(file_message['absolute_path'].encode('utf-8')).hexdigest()
            except:
                hash_str = 0

            insert_sql = "REPLACE INTO 'file_directory_table'('file_name', 'absolute_path', 'file_id', 'file_create_time', 'file_modify_time', 'file_size', 'file_type', 'status') " \
                         "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(file_message['file_name'],
                                                                                      file_message['absolute_path'],
                                                                                      hash_str,
                                                                                      file_message["file_create_time"],
                                                                                      file_message["file_modify_time"],
                                                                                      str(file_message["file_size"][0]) + file_message["file_size"][1],
                                                                                      file_message["file_type"],
                                                                                      0)
            status, result = self.db.execute_by_sql(insert_sql)
            # print(status, result)
        except:
            traceback.print_exc()
            pass

    def on_created(self, event):  # 文件创建
        self.get_file_attributes_all(event.src_path)

        # if event.is_directory:
        #     print("directory created:{0}".format(event.src_path))
        # else:
        #     print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):  # 文件删除
        self.db.execute_by_sql(self.updata_sql.format(str(event.src_path).replace("\\", "/").replace("\\\\", "/").replace("'", "\\\'").replace("\"", "\\\"")))
        # if event.is_directory:
        #     print("directory deleted:{0}".format(event.src_path))
        # else:
        #     print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):  # 文件更新
        self.get_file_attributes_all(event.src_path)
        # if event.is_directory:
        #     print("directory modified:{0}".format(event.src_path))
        # else:
        #     print("file modified:{0}".format(event.src_path))


if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, "D:/", True)
    observer.schedule(event_handler, "E:/", True)
    observer.schedule(event_handler, "F:/", True)
    observer.start()
    observer.schedule(event_handler, "C:/", True)
    # observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()