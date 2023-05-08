import time

import win32gui

from assets.sources import get_source
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data, compare_image


class Fight:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def is_fighting(self):
        """
        在内存中判断是否进入战斗
        :return:
        """
        img = crop_image_data(self.__screenshot(), (1012, 126), (1020, 378))
        rate = compare_image(img, get_source('fight_template'), channel_axis=True)
        if rate > 0.98:
            return True
        return False


class IsMovedTask:
    def __init__(self, hwnd):
        self._running = True
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)
        self.range = [(196, 195), (147, 600), (801, 84), (884, 641)]

    def terminate(self):
        self._running = False

    def __if_windows_in_screen(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def is_moving(self, sleep_time=1):
        if self.__if_windows_in_screen():
            crop_data_pre = []
            for crop_rectangle in self.range:
                x, y = crop_rectangle
                screenshot = winShot(self.hwnd)
                re = crop_image_data(screenshot, (x - 15, y - 15), (x + 15, y + 15))
                crop_data_pre.append(re)
            time.sleep(sleep_time)
            crop_data_later = []
            for crop_rectangle in self.range:
                x, y = crop_rectangle
                screenshot = winShot(self.hwnd)
                re = crop_image_data(screenshot, (x - 15, y - 15), (x + 15, y + 15))
                crop_data_later.append(re)
            for i in range(len(self.range)):
                rate = compare_image(crop_data_pre[i], crop_data_later[i])
                if rate >= 0.97:
                    logger.info("Player have stop move")
                    return False
            else:
                return True


isFight = Fight(WINDOW_ID)
isMoved = IsMovedTask(WINDOW_ID)
