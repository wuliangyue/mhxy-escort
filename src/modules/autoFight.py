# -*- coding: gbk -*-
import time

import pyautogui
import pywintypes
import win32gui

import config
import game_models.hoverModel as hm
from config import hover_list
from game_models.roleModel import get_role_center
from src.components.hover import hover
from src.components.status import isFight
from src.components.mouse import mouse
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img


class AutoFight:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)

    def __screenshot(self):
        return winShot(self.hwnd)

    def __task(self, fight_type=0, rate=0.85):
        if not self.__windows_in_screen():
            return False
        if fight_type == 0:
            if hover.normalNotification(rate):
                logger.info("存在弹窗：切割完毕")
                return True
        elif fight_type == 1:
            if hover.rewardNotification(rate):
                logger.info("存在奖励弹窗：切割完毕")
                return True

    def __windows_in_screen(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def __auto_click(self, fight_type=0, rate=0.85):
        if isFight.is_fighting():
            if not self.__task(fight_type, rate):
                return
            min_index = hm.model_predict(hover_list)
            result = match_img(self.__screenshot(), hover_list[min_index], 10, 10, 0.98)
            if result[3] is None:
                return
            target_x, target_y = result[3]['result']

            # 利用yolo5 检测出头部
            xcenter, ycenter = get_role_center(hover_list[min_index])
            target_x = target_x + xcenter - 45
            target_y = target_y + ycenter - 70
            logger.info(f' 点击坐标为 > x：{target_x} < ; y：{target_y}')

            if target_x == 0 and target_y == 0:
                logger.warning('匹配失败弹窗点击失败')
            else:
                logger.info('开始点击弹窗')
                mouse.move_click(target_x, target_y)
                time.sleep(0.5)
                if hover.secondNotification(rate):
                    min_index = hm.model_predict(hover_list)
                    result = match_img(self.__screenshot(), hover_list[min_index], 10, 10, 0.98)
                    if result[3] is None:
                        return
                    target_x, target_y = result[3]['result']

                    # 利用yolo5 检测出头部
                    xcenter, ycenter = get_role_center(hover_list[min_index])
                    target_x = target_x + xcenter - 45
                    target_y = target_y + ycenter - 70

                    if target_x == 0 and target_y == 0:
                        logger.warning('匹配失败弹窗点击失败')
                    else:
                        mouse.move_click(target_x, target_y)

    def __auto_action(self):
        if isFight.is_fighting():
            if isFight.is_need_fight_action():
                pyautogui.hotkey("alt", config.player_action)
                pyautogui.hotkey("alt", config.bb_action)
                time.sleep(1)
            return True
        return False

    def __automation(self, fight_type, rate):
        while True:
            self.__auto_click(fight_type, rate)
            self.__auto_action()

    def run(self, fight_type=0, rate=0.85):
        logger.info("Script start to load auto fight model")
        hm.model_load()
        while True:
            try:
                self.__automation(fight_type, rate)
            except Exception as e:
                if type(e) == pywintypes.error:
                    if e.args[0] == 1400:
                        logger.info("Game was closed")
                        return


AutoFightTask = AutoFight(WINDOW_ID)


def auto_task():
    AutoFightTask.run()


if __name__ == '__main__':
    auto_task()
