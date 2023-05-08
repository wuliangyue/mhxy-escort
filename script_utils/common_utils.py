import os

from script_utils.loggerConfig import logger


def findfiles(path):
    result = []
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 循环判断每个元素是否是文件夹还是文件，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if not os.path.isdir(cur_path):
            result.append(file)
    return result


def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f'文件夹创建 -> {path}')
