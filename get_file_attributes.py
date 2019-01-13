import os


def get_FileSize(filePath):  # 获取文件大小
    try:
        fsize = os.path.getsize(filePath)
    except:
        fsize = 0
    return dynamic_unit(fsize)

def dynamic_unit(size):  # 动态获取大小的单位，GB
    # if size > 1073741824:  # BB
    #     return (round(size/float(1073741824), 2), "BB")
    #
    # elif size > 1073741824:  # YB
    #     return (round(size/float(1073741824), 2), "YB")
    #
    # elif size > 1.180591620717411e+21:  # ZB
    #     return (round(size/float(1.180591620717411e+21), 2), "ZB")
    #
    # elif size > 1.152921504606847e+18:  # EB
    #     return (round(size/float(1073741824), 2), "EB")
    #
    # elif size > 1125899906842624:  # PB
    #     return (round(size/float(1125899906842624), 2), "PB")
    #
    # elif size > 1099511627776:  # TB
    #     return (round(size/float(1099511627776), 2), "TB")

    if size > 1073741824:  # GB
        return (round(size/float(1073741824), 2), "GB")

    elif size > 1048576:  # MB
        return (round(size/float(1048576), 2), "MB")

    elif size > 1024:  # KB
        return (round(size/float(1024), 2), "KB")

    else:
        return (round(size), "b")

def get_FileModifyTime(filePath):  # 获取文件修改时间
    t_FileModifyTime = os.path.getmtime(filePath)
    return int(t_FileModifyTime)

def get_FileCreateTime(filePath):
    t_FileModifyTime = os.path.getctime(filePath)
    return int(t_FileModifyTime)


if __name__ == '__main__':
    # print(get_FileModifyTime("file_monitoring.py"))
    # print(get_FileCreateTime("file_monitoring.py"))
    # print(os.path.getatime("file_monitoring.py"))
    # print(get_FileSize("file_monitoring.py"))
    print(os.path.split("C:/Users/luoxi/AppData/Local/Finkit/ManicTime/Screenshots/2019-01-12/2019-01-12_17-05-55_08-00_1840_1098_148404.thumbnail.png"))
