'''
文件监控
'''
import traceback

import os
import sys

import time
import string

import psutil

import win32file
import win32con

from threading import Thread

from linkSqlite import DBSqlite

from get_file_attributes import *

from file_event_handler import FileEventHandler
from watchdog.observers import Observer
from watchdog.events import *

import ctypes

whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)



class FileMonitoring:
    def __init__(self):
        print("Start!")

        self.drive_letter = [] # 已进行监控的目录
        self.drive_letter_new = []  # 需要进行全盘扫描的分区

        self.db = DBSqlite()

        self.observer = Observer()
        self.event_handler = FileEventHandler()
        self.observer.start()

        count = 0
        while True:
            self.get_drive_letter()
            time.sleep(20 * 60)  # 每隔20分钟重新扫描一遍分区信息
            count += 1
            if count == 3:  # 每隔一小时，清理不需要的文件
                self.db.clean_up_redundant_data()
                count = 0
            # self.observer.stop()
        # self.observer.join()

    def get_drive_letter(self):   # 获取所有的分区号

        drive_list_message = psutil.disk_partitions()  # 获取分区信息
        for drive in drive_list_message:
            if drive.device not in self.drive_letter:
                # print(drive.device, "  Start")
                self.drive_letter.append(drive.device)  # 添加到已建立链接的位置
                self.observer.schedule(self.event_handler, drive.device, True)  # 订阅新的监控

                # self.create_file_index_one(drive.device)  # 单线程建立全部索引

                # create_index = Thread(None, self.create_file_index_one, None, (drive.device,))  # 建立全区索引
                # create_index.daemon = True
                # create_index.start()

    def get_file_attributes_all(self, root, file):  # 获取文件的完整属性
        try:
            file = file.replace("'", "\\\'").replace("\"", "\\\"")
            file_message = {}
            file_message["file_name"] = file  # 文件名
            file_message["absolute_path"] = os.path.join(root, file).replace("\\", "/").replace("\\\\", "/")  # 绝对路径
            file_message["file_modify_time"] = get_FileModifyTime(file_message["absolute_path"])  # 修改时间
            file_message["file_size"] = get_FileSize(file_message["absolute_path"])  # 文件大小

            try:  # 文件属性
                file_message["file_type"] = os.path.splitext(file_message["absolute_path"])[1][1:]
            except:
                file_message["file_type"] = None

            file_message["file_create_time"] = get_FileCreateTime(file_message["absolute_path"])
            return file_message
        except:
            pass


    def create_file_index_one(self, drive):  # 建立磁盘文件索引(静态,单个分区)
        # a = time.time()
        try:
            count = 0
            file_list = []
            for root, dirs, files in os.walk(drive):
                # print(root)
                for file in files:
                    file_list.append(self.get_file_attributes_all(root, file))
                    count += 1
                if count > 25000:
                    while not self.db.initial_file_index(file_list):  # 失败则重试
                        if os.path.exists(drive):  # 如果分区消失，则停止
                            pass
                        else:
                            break
                    del file_list
                    file_list = []
                    count = 0

            while not self.db.initial_file_index(file_list):  # 失败则重试
                if os.path.exists(drive):  # 如果分区消失，则停止
                    pass
                else:
                    break
            # print(drive, "索引建立完毕", file_list.__len__())
        except:
            traceback.print_exc()
            # print("索引建立失败")
            pass

        # print(drive, time.time() - a)

    def monitor_file_changes(self, drive_letter):  # 监控文件变化，调用Windows API(增删改)
        ACTIONS = {
            1: "Created",
            2: "Deleted",
            3: "Updated",
            4: "Renamed from something",
            5: "Renamed to something"
        }

        FILE_LIST_DIRECTORY = win32con.GENERIC_READ | win32con.GENERIC_WRITE
        path_to_watch = drive_letter
        # print("查找到分区", drive_letter)
        hDir = win32file.CreateFile(
            path_to_watch,
            FILE_LIST_DIRECTORY,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )

        while True:
            # https://docs.microsoft.com/en-us/windows/desktop/api/WinBase/nf-winbase-readdirectorychangesw
            results = win32file.ReadDirectoryChangesW(
                hDir,
                # handle: Handle to the directory to be monitored. This directory must be opened with the FILE_LIST_DIRECTORY access right.
                1024,  # size: Size of the buffer to allocate for the results.
                True,
                # bWatchSubtree: Specifies whether the ReadDirectoryChangesW function will monitor the directory or the directory tree.
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None)
            print(results)
            for action, file in results:
                full_filename = os.path.join(path_to_watch, file)
                print(full_filename, ACTIONS.get(action, "Unknown"))  # 文件名，更新状态


if __name__ == '__main__':
    b = FileMonitoring()
