from datetime import datetime, date

import win32gui

from assets.sources import get_source, npc_data
from script_utils.cnOcr import cn_ocr, get_closed_string
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterTaskRed
from script_utils.matchTemplate import match_img, crop_image_data
from src.components.window import WINDOW_ID


class GameTask:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_windows_in_screen(self) -> bool:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def get_task_text(self):
        screenshot = self.__screenshot()
        result = match_img(screenshot, get_source('task_flag'), 10, 10, 0.95)
        task_text = ""
        if result[3] is None:
            return task_text
        left_up = result[3]['rectangle'][0]
        right_down = result[3]['rectangle'][3]
        crop_data = crop_image_data(screenshot, left_up=(left_up[0] - 136, left_up[1] + 47),
                                    right_down=(right_down[0], right_down[1] + 58))
        crop_data = hsvFilterTaskRed(crop_data)
        result = cn_ocr.ocr(crop_data)
        if result:
            for data in result:
                task_text += data['text']
        return task_text


Game = GameTask(WINDOW_ID)


def escort_npc():
    game_info = Game.get_task_text()
    if game_info == "":
        return ""
    return get_closed_string(game_info, list(npc_data.keys()))


TaskInfo = {
    "押镖": escort_npc,
}


def get_task_info(TaskName):
    return TaskInfo[TaskName]()
