import random
import time

import pyautogui

from assets.sources import npc_data, get_source
from script_utils.csvUtil import escort_data
from script_utils.grabScreen import winShot
from script_utils.matchTemplate import match_img
from src.components.mouse import mouse
from src.components.status import isFight
from src.components.window import WINDOW_ID, NAME
from src.modules.check import click_check
from src.modules.map import MapTask, click_button
from src.modules.npc import NpcTask
from src.modules.props import PropsFunction
from src.modules.task import get_task_info, escort_npc

TaskNpc = "郑镖头"
TaskType = "押镖"
TaskLocation = "长风镖局"


def fly_to(location):
    now = MapTask.GetMapName()
    if now == location:
        return
    PropsFunction.openProps()
    time.sleep(0.5)
    res = PropsFunction.findProps("黄色飞行旗")
    if not res:
        return fly_to(location)
    mouse.move(res[0], res[1])
    pyautogui.rightClick()
    time.sleep(0.5)
    screenshot = winShot(WINDOW_ID)
    result = match_img(screenshot, get_source('b_j_flag'), 10, 10, 0.95)
    if result[3] is None:
        return
    mouse.move_click(result[3]['result'][0] + 240, result[3]['result'][1] - 23)
    PropsFunction.closeProps()
    time.sleep(1)
    if MapTask.GetMapName() != "长安城":
        return fly_to(location)
    mouse.move_click(582 + random.randint(1, 5) * random.choice([-1, 1]),
                     360 + random.randint(1, 5) * random.choice([-1, 1]), bias=5)
    time.sleep(2)
    mouse.move_click(592 + random.randint(1, 50) * random.choice([1]),
                     253 + random.randint(1, 20) * random.choice([-1, 1]), bias=20)
    time.sleep(3)


def get_escort_task(level=4):
    task_info = get_task_info(TaskType)
    if task_info:
        return
    fly_to(TaskLocation)
    NpcTask.go_npc(TaskNpc)
    # click task npc
    result = NpcTask.findNpc(TaskNpc)
    if not result:
        return
    mouse.move_click(result[0], result[1])
    time.sleep(3)
    # click task button
    check_result = click_check(retry=30, sleep_time=30)

    if check_result:
        result = NpcTask.findNpc(TaskNpc)
        if not result:
            return
        mouse.move_click(result[0], result[1])
        time.sleep(3)

    if not click_button(f"escort_{level}"):
        return
    time.sleep(5)
    if not click_button("reserves"):
        return
    time.sleep(5)
    pyautogui.leftClick()
    return 1


def finish_escort_task(npc):
    loc = npc_data[npc]["location"]
    MapTask.MoveToTarget(loc, "None")
    while True:
        while isFight.is_fighting():
            time.sleep(1)
        task_info = get_task_info(TaskType)
        if not task_info:
            return
        NpcTask.go_npc(npc)
        result = NpcTask.findNpc(npc)
        if not result:
            continue
        mouse.move(result[0], result[1])
        pyautogui.hotkey("alt", "g")
        time.sleep(0.1)
        pyautogui.leftClick()
        time.sleep(4)
        if not PropsFunction.isPropsToNpc():
            pyautogui.rightClick()
            time.sleep(0.1)
            continue
        result = PropsFunction.findProps("四级镖银")
        if not result:
            continue
        mouse.move_click(result[0], result[1])
        time.sleep(0.1)

        # press give button
        result = click_button("confirm_give")
        if not result:
            continue
        time.sleep(3)
        pyautogui.leftClick()
    escort_data.add_task_time(NAME)


def escort_one_time():
    while get_escort_task() is None:
        continue
    npc = escort_npc()
    finish_escort_task(npc)


