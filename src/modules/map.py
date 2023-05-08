import random
import time

import pyautogui
import win32gui

from assets.sources import location_data, get_source, proxies_data, write_json, join_path
from script_utils.cnOcr import cn_ocr, get_closed_string, get_chinese_text, get_number
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterLocationWhite, hsvFilterErrorYellow
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data, match_img
from script_utils.pathSearch import path_search
from src.components.status import isFight, isMoved
from src.components.window import WINDOW_ID, set_parent_foreground
from src.components.mouse import mouse


def click_button(button_name=None):
    if button_name is None or button_name == "":
        return False
    result = match_img(winShot(WINDOW_ID), get_source(button_name), 10, 10, 0.95)[3]
    if result is not None:
        x, y = result['result']
        mouse.move_click(x, y)
        return True
    return False


def click_button_v2(button_image_name):
    if button_image_name is None or button_image_name == "":
        return False
    result = match_img(winShot(WINDOW_ID), join_path('move', button_image_name), 10, 10, 0.95)[3]
    if result is not None:
        x, y = result['result']
        mouse.move_click(x, y)
        return True
    return False


def click_transport_npc(now, target):
    action = location_data[now][target]["action"]
    if "template" and "mask" in action:
        mask_name = action["mask"]
        template = join_path('move', action["template"])
        if mask_name is not None:
            mask = join_path('move', mask_name)
            result = match_img(winShot(WINDOW_ID), template, 10, 10, 0.92, mask)[3]
            if result is not None:
                x, y = result['result']
                x, y = x, y - 70
                mouse.move_click(x, y)
                time.sleep(1)
                return True, (x, y)
        else:
            result = match_img(winShot(WINDOW_ID), template, 10, 10, 0.92)[3]
            if result is not None:
                x, y = result['result']
                x, y = x, y
                mouse.move_click(x, y)
                time.sleep(1)
                return True, (x, y)
    return False, (None, None)


def get_yellow_text() -> [(int, int), (int, int)]:
    x, y = mouse.get_mouse_point()
    corp = crop_image_data(winShot(WINDOW_ID), (x - 38, y - 28),
                           (x + 46, y - 8))
    re = hsvFilterErrorYellow(corp)
    raw = cn_ocr.ocr_for_single_line(re)
    number_list = get_number(raw)
    if len(number_list) < 2:
        return [(0, 0), (x, y)]
    return [(int(number_list[0]), int(number_list[1])), (x, y)]


class Map:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_windows_in_screen(self) -> bool:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def __close_exit_box(self):
        result_1 = match_img(self.__screenshot(), get_source('map_exit_flag'), 10, 10, 0.99)[3]
        result_2 = match_img(self.__screenshot(), get_source('map_exit_flag_2'), 10, 10, 0.99)[3]
        if result_1 is not None:
            x, y = result_1['result']
            mouse.move_click(x, y)
            return
        if result_2 is not None:
            x, y = result_2['result']
            mouse.move_click(x, y)
            return

    def GetMapName(self) -> str:
        screenshot = self.__screenshot()
        img = crop_image_data(screenshot, left_up=(18, 24),
                              right_down=(140, 34))
        raw_text = cn_ocr.ocr_for_single_line(hsvFilterLocationWhite(img, mask=True))['text']
        chinese_text = get_chinese_text(raw_text)
        return get_closed_string(chinese_text, [location for location in location_data.keys()])

    def __is_map_open(self) -> bool:
        screenshot = self.__screenshot()
        result = match_img(screenshot, get_source('map_flag'), 10, 10, 0.95)
        if result[3] is not None:
            return True
        return False

    def openMap(self, retry=2):
        retry_time = retry
        while True:
            if retry_time <= 0:
                break
            if self.__if_windows_in_screen():
                if self.__is_map_open():
                    logger.info("小地图已经开")
                    break
                else:
                    logger.info("小地图已经关闭，正在打开")
                    pyautogui.press('tab')
                    time.sleep(0.1)
            else:
                logger.info("梦幻不在当前窗口")
                set_parent_foreground(self.hwnd)
                time.sleep(2)
                retry_time -= 1
        return

    def MapMove(self, x, y, region, next=None):
        """
            OCR 得方法去移动点击小地图上点，在线程中每次加载会很慢
            :param next:
            :param x:
            :param y:
            :param region:
            :return:

            """
        logger.info("目的地{}:{}".format(region, (x, y)))
        if region in ["轮回司"]:
            return
        self.openMap()
        logger.info("开始进行地图点击")
        if next in ["狮驼岭"]:
            self.__close_exit_box()
        # Mouse().move(600, 550)
        if region in proxies_data:
            dx = proxies_data[region]['dx']
            dy = proxies_data[region]['dy']
            if 'start_point' in proxies_data[region]:
                start = proxies_data[region]['start_point'][0]
                bias_x = proxies_data[region]['start_point'][1]
                bias_y = proxies_data[region]['start_point'][2]

                result = match_img(self.__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
                if result is None:
                    logger.info("未找到小地图标识")
                    return
                map_xy = result['result']
                x1, y1 = start[0], start[1]
                x2, y2 = map_xy[0] + bias_x, map_xy[1] + bias_y
                target_x = (x - x1) * dx + x2
                target_y = (y - y1) * dy + y2
            else:
                xs = random.randint(490, 510)
                ys = random.randint(340, 360)
                mouse.client_move(xs, ys)
                time.sleep(1)
                (x1, y1), (x2, y2) = get_yellow_text()
                if x1 == 0 and x2 == 0:
                    return
                start = (x1, y1)
                result = match_img(self.__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
                if result is None:
                    logger.info("未找到小地图标识")
                    return
                map_xy = result['result']
                bias_x = x2 - map_xy[0]
                bias_y = y2 - map_xy[1]
                proxies_data.update({region: {'start_point': [start, bias_x, bias_y], 'dx': dx, 'dy': dy}})
                write_json(proxies_data, 'proxies')
                target_x = (x - x1) * dx + x2
                target_y = (y - y1) * dy + y2

        else:
            xs = random.randint(490, 510)
            ys = random.randint(340, 360)
            mouse.locked_client_move(xs, ys)
            time.sleep(1)
            logger.info("正在记录地图比例尺")
            (x1, y1), (x2, y2) = get_yellow_text()
            if x1 == 0:
                return
            dddd = 100
            yyyy = 100
            mouse.move(x2 + dddd, y2 + yyyy, bias=0)
            time.sleep(2)
            (x3, y3), (x4, y4) = get_yellow_text()
            if x3 == 0:
                return
            dx = dddd / abs(x1 - x3)
            dy = -yyyy / abs(y1 - y3)
            proxies_data.update({region: {'dx': dx, 'dy': dy}})
            target_x = (x - x3) * dx + x4
            target_y = (y - y3) * dy + y4
            write_json(proxies_data, 'proxies')
            logger.info("{}地图比例尺记录结束,dx:{},dy:{}".format(region, dx, dy))
        logger.info(f"开始进行地图点击{target_x, target_x}")
        mouse.move_click(round(target_x), round(target_y), bias=2)
        time.sleep(2)
        pyautogui.press('tab')
        return 1
        pass

    def MoveToTarget(self, end, name):
        # 是否停止移动
        if name == '':
            return
        # 到达目的场景，移动
        previous_city = ''
        while True:
            while isFight.is_fighting():
                logger.info("战斗中，等待战斗结束")
                time.sleep(1)
            now_city = self.GetMapName()

            if now_city == end:
                logger.info("已到达目的地，退出自动寻路")
                break

            # 有没有需要点击的东西
            if previous_city == now_city:
                if click_button('yes_i_will_go'):
                    now_city = self.GetMapName()
                # 有没有干扰项目
                else:
                    click_button('close_button_x')

            previous_city = now_city
            path = path_search.a_star_algorithm(now_city, end)

            next_city = path[1]
            # 点击地图
            info = location_data[now_city][next_city]
            x, y = info["XY"]
            if info["action"]["type"] == 3:
                xy_list = info["action"]["xy"]
                for xy in xy_list:
                    x, y = xy
                    # 增加随机，避免一直点一个点
                    mouse.move_click(x, y, bias=10)
                    click_times = random.randrange(0, 3, 1)
                    while click_times > 0:
                        mouse.left_click()
                        click_times -= 1
                    time.sleep(random.uniform(3, 4))
                    map_name = self.GetMapName()
                    if map_name == next_city:
                        break
                continue

            s = self.MapMove(x, y, now_city, next=next_city)

            if s is None:
                continue

            logger.info("正在前往目的地")
            skip = False
            while True:
                if isFight.is_fighting():
                    skip = True
                    break
                if not isMoved.is_moving():
                    break
            if skip:
                continue

            pyautogui.hotkey('alt', 'h')
            pyautogui.press('f9')
            if info["action"]["type"] == 0:
                x, y = info["action"]["xy"]
                # 增加随机，避免一直点一个点
                # x, y = get_random_xy(x, y)
                mouse.move_click(x, y)
            else:
                action = info["action"]
                click_result_1, (x_n, y_n,) = click_transport_npc(now_city, next_city)
                if not click_result_1:
                    continue
                if "button" in action:
                    click_result_2 = click_button_v2(action["button"])
                else:
                    click_result_2 = click_button('yes_i_will_go')
                if not click_result_2:
                    if click_result_1:
                        mouse.move_click(x_n - 100, y_n)
                        time.sleep(3)
                        pyautogui.hotkey('alt', 'h')
                        pyautogui.press('f9')
                        time.sleep(1)
                        click_result, (x_n, y_n) = click_transport_npc(now_city, next_city)
                        if not click_result:
                            logger.info("没有找到传送NPC")
                            continue
                        if "button" in action:
                            click_result_2 = click_button_v2(action["button"])
                        else:
                            click_result_2 = click_button('yes_i_will_go')
                        if not click_result_2:
                            logger.info("没有找到传送按钮")
                            continue
                        time.sleep(2)
                        continue
            time.sleep(3)
        pass


MapTask = Map(WINDOW_ID)

if __name__ == '__main__':
    time.sleep(2)
    MapTask.MoveToTarget("化生寺", "11")
