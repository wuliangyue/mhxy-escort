import math
import os
import time
import random
import pyautogui
import win32gui
import cv2
from assets.sources import npc_data, basedir
from script_utils.loggerConfig import logger
from src.components.mouse import mouse
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.matchTemplate import match_img
from src.modules.map import MapTask


class NPC:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_windows_in_screen(self) -> bool:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def findNpc(self, name, rate=0.95):
        pyautogui.press("f9")
        time.sleep(1)
        npc_info = npc_data[name]
        template = os.path.join(basedir, 'npc', npc_info["template"])
        rate_list = {
            "镇元大仙": 0.8
        }
        if "mask" in npc_info:
            mask = npc_data[name]['mask']
            mask = os.path.join(basedir, 'npc', mask)
            if name in ["郑镖头", "白虎堂总管", "黑无常", "店小二"]:
                logger.info(f"mask->{mask}, template->{template}")
                result = match_img(self.__screenshot(), template, 10, 10, rate, mask=mask, method=cv2.TM_SQDIFF_NORMED)
            else:
                result = match_img(self.__screenshot(), template, 10, 10, rate, mask=mask)
            if result[3]:
                x, y = result[3]['result']
                return x - 2, y - 80
        else:
            if name in rate_list.keys():
                rate = rate_list[name]
            result = match_img(self.__screenshot(), template, 10, 10, rate)
        if result[3]:
            x, y = result[3]['result']
            if name == "镇元大仙":
                return x - 20, y
            return x, y

    def go_npc(self, name):
        npc_info = npc_data[name]
        location = npc_info['location']
        MapTask.MoveToTarget(location, "None")
        location_flag = npc_info['location_flag']
        if len(location_flag) == 0:
            return
        if name not in ["杨戬", "李靖", "菩提祖师", "秦琼", "三大王", "冰冰姑娘", "郑镖头", "观音姐姐", "白虎堂总管"]:
            return
        if name == "菩提祖师":
            mouse.move_click(731, 135)
            time.sleep(2)
            mouse.move_click(791, 135)
            time.sleep(6)
            return
        for template in location_flag:
            template = os.path.join(basedir, 'npc', template)
            pyautogui.press('f9')
            time.sleep(1)
            result = match_img(self.__screenshot(), template, 10, 10)
            logger.info("close to {}".format(name))
            if result[3]:
                x, y = result[3]['result']
                if name == "郑镖头":
                    print("npc ----------")
                    r = random.randrange(80, 100, 5)
                    bias = random.randrange(0, r, 5) * random.choice([-1, 1])
                    abs_x_bias = math.sqrt(r * r - bias * bias)
                    x_bias = abs_x_bias * random.choice([-1, 1])
                    mouse.move_click(x + x_bias, y + bias, bias=10)
                else:
                    mouse.move_click(x, y, bias=10)
                time.sleep(5)


NpcTask = NPC(WINDOW_ID)

