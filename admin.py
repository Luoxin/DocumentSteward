'''
获取管理员权限
'''
import traceback
import time
from threading import Thread

import psutil

from file_monitoring import FileMonitoring

import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_procs_by_name(name):
    "Return a list of processes matching 'name'."
    ls = []
    for p in psutil.process_iter(attrs=['name']):
        if p.info['name'] == name:
            ls.append(p)
    return ls

if __name__ == '__main__':
    try:
        if is_admin():
            ls = find_procs_by_name("File_monitoring.exe")
            if ls.__len__() == 2:  #  如果不存在其他正在执行的文件索引服务，则执行，否则退出
                FileMonitoring()

            # indexing_engine = Thread(None, FileMonitoring, None, ())  # 建立全区索引
            # indexing_engine.daemon = True
            # indexing_engine.start()


            # 将要运行的代码加到这里
        else:
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            else:#in python2.x
                ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
    except:
        print("启动管理员方式运行失败，请尝试手动启动管理员方式运行")