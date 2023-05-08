# -*- coding: utf-8 -*-
import random
import time

import cv2
import portalocker
import pyautogui
import win32gui

from assets.sources import get_source
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img


def start_point(x_min, y_min, x_max, y_max):
    """
    随机生成一个起始点
    :param x_min:
    :param y_min:
    :param x_max:
    :param y_max:
    :return: 坐标
    """
    return random.uniform(x_min, x_max), random.uniform(y_min, y_max)


def rel_move(x, y):
    pyautogui.moveRel(int(x), int(y), duration=random.random())


def if_arrived(x1, y1, x2, y2, bias=3):
    """
    判断坐标1和坐标二是否一致
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :param bias:
    :return:
    """
    x_abs = abs(x1 - x2)
    y_abs = abs(y1 - y2)
    return x_abs <= bias and y_abs <= bias


def if_mouse_using():
    f = open(get_source("mouse_status"), 'r')
    try:
        status = f.read().strip()
    except PermissionError:
        return True
    f.close()
    if status == '1':
        return True
    else:
        return False


def set_mouse_not_using():
    f = open(get_source("mouse_status"), 'w')
    f.write('0')
    f.close()


def locked_mouse(function):
    """
    装饰器，在操作鼠标时对鼠标进行占用，防止多线程/多进程时鼠标有多个控制源
    :param function:
    :return:
    """

    def inner(*args, **kwargs):
        while True:
            if not if_mouse_using():
                break
        # 告诉鼠标被控制
        f = open(get_source("mouse_status"), 'w')
        portalocker.lock(f, portalocker.LOCK_EX)  # 加锁
        f.write('1')
        function(*args, **kwargs)
        f.write('0')
        f.close()

    return inner


class Mouse:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)

    def __screenshot(self):
        return winShot(self.hwnd)

    def __client_move(self, x, y):
        if not self.__if_windows_in_screen():
            logger.warning("梦幻西游不在当前窗口")
            return
        x, y = win32gui.ClientToScreen(self.hwnd, (int(x), int(y)))
        pyautogui.moveTo(x, y)
        time.sleep(0.15)
        return x, y

    @locked_mouse
    def locked_client_move(self, x, y):
        if not self.__if_windows_in_screen():
            logger.warning("梦幻西游不在当前窗口")
            return
        x, y = win32gui.ClientToScreen(self.hwnd, (int(x), int(y)))
        pyautogui.moveTo(x, y)
        time.sleep(0.15)
        return x, y

    def get_mouse_point(self, retry=5, method=cv2.TM_CCORR_NORMED):
        """
        获取计算出来的坐标，(包含截图顶部)
        :param
        :return: 矩形左上角坐标，即鼠标点点的坐标
        """
        result = match_img(self.__screenshot(), get_source("mouse_template"), 10, 10, 0.98, mask=None, method=method)
        s_x, s_y = 500, 300
        while result[3] is None and retry >= 0:
            s_x, s_y = start_point(200, 900, 200, 600)
            self.__client_move(s_x, s_y)
            result = match_img(self.__screenshot(), get_source("mouse_template"), 10, 10, 0.98, mask=None,
                               method=method)
            retry = retry - 1
        if result[3] is None:
            return s_x, s_y
        else:
            x, y = result[3]['rectangle'][0]
            return x - 11, y - 12

    def __mouse_in_window(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        x, y = pyautogui.position()
        if left <= x < right and top <= y < bottom:
            return True
        else:
            return False

    def __go_game_rectangle(self, x, y, bias=3, count=10):
        x = int(x)
        y = int(y)
        if x < 50 or x > 940 or y < 50 or y > 700:
            if not self.__mouse_in_window():
                self.__client_move(start_point(200, 900, 200, 600)[0], start_point(200, 900, 200, 600)[1])
            mouse_x, mouse_y = self.get_mouse_point()
            if not if_arrived(x, y, mouse_x, mouse_y, bias=bias):
                dxs = int((x - mouse_x) / 1.3)
                dys = int((y - mouse_y) / 1.3)
                rel_move(dxs, dys)
            else:
                return 1
        else:
            self.__client_move(x, y)
        x_moved, y_moved = self.get_mouse_point()

        # 逼进坐标
        s_count = count
        while not if_arrived(x, y, x_moved, y_moved, bias=bias) and s_count >= 1:
            if not self.__if_windows_in_screen():
                return
            if not self.__mouse_in_window():
                self.__client_move(start_point(200, 900, 200, 600)[0], start_point(200, 900, 200, 600)[1])
            if int((x - x_moved) / 1.06) == 0 or int((y - y_moved) / 1.06) == 0:
                rel_move(int((x - x_moved)), int((y - y_moved)))
            else:
                rel_move(int((x - x_moved) / 1.06), int((y - y_moved) / 1.06))
            x_moved, y_moved = self.get_mouse_point()
            s_count = s_count - 1
            if s_count <= 0:
                logger.info("鼠标移动一个地方超出最大次数,可移动次数")
                return
        return 1

    def __if_windows_in_screen(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def __left_click(self):
        return pyautogui.leftClick()

    def __right_click(self):
        return pyautogui.rightClick()

    @locked_mouse
    def move(self, x, y, bias=3):
        self.__go_game_rectangle(x, y, bias=bias)
        return self.get_mouse_point()

    @locked_mouse
    def move_click(self, x, y, bias=3):
        self.__go_game_rectangle(x, y, bias=bias)
        self.__left_click()
        return self.get_mouse_point()

    @locked_mouse
    def left_click(self):
        return self.__left_click()

    @locked_mouse
    def right_click(self):
        return self.__right_click()


set_mouse_not_using()
mouse = Mouse(WINDOW_ID)
