import logging
import os
import time

import colorlog

from config import root_dir

log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def day_str():
    localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 系统当前时间年份
    year = time.strftime('%Y', time.localtime(time.time()))
    # 月份
    month = time.strftime('%m', time.localtime(time.time()))
    # 日期
    day = time.strftime('%d', time.localtime(time.time()))

    return f'{year}_{month}_{day}'


def logger_config(logging_name):
    """
    配置log
    :param logging_name: 记录中name，可随意
    :return:
    """
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    log_path = os.path.join(root_dir, 'logs', day_str() + '.txt')
    dir_create(os.path.join(root_dir, 'logs'))
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter(
        '[%(asctime)s][%(name)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- '
        '%(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s][%(name)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %('
            'message)s',
        datefmt='%Y-%m-%d  %H:%M:%S',
        log_colors=log_colors_config
    )
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(console_formatter)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'{path} is not exist, directory created -> {path}')


logger = logger_config("Script Running")

if __name__ == '__main__':
    logger.info('test log')
