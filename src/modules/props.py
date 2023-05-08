import os.path
import random
import time

import pyautogui
import win32gui

from assets.sources import get_source, basedir, props_data
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.mouse import mouse
from src.components.window import WINDOW_ID


class Props:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_windows_in_screen(self) -> bool:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def openProps(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_flag'), 10, 10, rate)
        if result[3] is None:
            logger.info("道具行囊未打开，打开道具行囊")
            pyautogui.hotkey('alt', 'e')
            time.sleep(0.5)
            return
        else:
            logger.info("道具行囊已经打开,confidence:{}".format(result[3]['confidence']))
            return

    def closeProps(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_flag'), 10, 10, rate)
        if result[3] is None:
            return
        else:
            pyautogui.hotkey('alt', 'e')
            time.sleep(0.5)
            return

    def findProps(self, name, rate=0.95):
        template = os.path.join(basedir, 'props', props_data[name])
        result = match_img(self.__screenshot(), template, 10, 10, rate)
        if result[3] is None:
            return
        return result[3]['result']

    def closeButtonToNpc(self):
        return self.findProps("确定给予")

    def isPropsToPlayer(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_to_player'), 10, 10, rate)
        if result[3] is None:
            return
        return result[3][result]

    def isPropsToNpc(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_to_npc'), 10, 10, rate)
        if result[3] is None:
            return
        return result[3][result]


PropsFunction = Props(WINDOW_ID)
