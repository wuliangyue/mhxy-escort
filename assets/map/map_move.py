import math
import os
import random
import time

import json

import pyautogui
import win32gui

import common
import constant
import utils_local

from game_common_action.mouse import client_lock_mouse_move, move_click_with_fight, move_with_fight, left_click, \
    right_click, release
from game_common_action.props import Props
from image_Identification.findImage import is_open_map, get_chuan_song_npc, get_chuansong_xy, if_check_exit_box, \
    find_map_flag_xy, get_map_flag_2
from game_common_action.fight import IsMovedTask
from search import path_search
from game_mission.findNpc import NPC
from image_Identification.findText import get_xy_in_map, get_map_name, get_misson_text, get_mission_type

k_maple = json.load(open(constant.proxies, 'r', encoding='utf-8'))

logger = utils_local.logger_config("地图移动/交镖任务")

npc = NPC()
props = Props()
map_loc = json.load(open(constant.status_json, 'r', encoding='utf-8'))


def fighting():
    f = open(constant.fight_status, 'r')
    status = f.read().strip()
    f.close()
    if status == '1':
        return True
    else:
        return False


def write_to_json(ips, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ips, f, indent=4, ensure_ascii=False)


def close_map():
    if common.if_mhxy_in_srceen():
        if is_open_map():
            pyautogui.press("tab")
            time.sleep(0.05)


def open_map():
    count = 2
    while True:
        if count <= 0:
            break
        if common.if_mhxy_in_srceen():
            if is_open_map():
                logger.info("小地图已经开")
                break
            else:
                logger.info("小地图已经关闭，正在打开")
                # if count <= 1:
                #     move_with_fight(int(random.uniform(100, 700)), int(random.uniform(100, 200)), bias=30)
                #     result = get_map_flag_2()
                #     while result is not None:
                #         x, y = result[0], result[1]
                #         move_with_fight(result[0], result[1])
                #         if x < 500:
                #             pyautogui.dragRel(50, 0, duration=1)
                #             left_click()
                #         if y < 300:
                #             pyautogui.dragRel(0, 50, duration=1)
                #             left_click()
                #         move_with_fight(int(random.uniform(100, 700)), int(random.uniform(100, 200)), bias=30)
                #         result = get_map_flag_2()
                #         if is_open_map():
                #             break
                pyautogui.press('tab')
        else:
            logger.info("梦幻不在当前窗口")
            try:
                win32gui.SetForegroundWindow(common.get_mhxy_window_by_id())
            except Exception as e:
                logger.error("设置窗口主屏幕报错")
        count -= 1
        time.sleep(0.1)


def get_task_nums():
    f = open(constant.yabiao_status, 'r', encoding='GBK')
    status = f.read().strip()
    f.close()
    status = status.split(' ')
    now = utils_local.day_str()
    user = common.title
    if now != status[0] or user != status[2]:
        f = open(constant.yabiao_status, 'w')
        f.write(now + ' ' + '0' + ' ' + common.title)
        f.close()
        return 0
    else:
        return int(status[1])


def add_task_nums():
    n = get_task_nums()
    f = open(constant.yabiao_status, 'w', encoding='GBk')
    f.write(utils_local.day_str() + ' ' + str(n + 1) + ' ' + common.title)
    f.close()


def get_random_xy(x, y):
    """
    给出固定的坐标，然后使用生成这个范围内的坐标
    :param x:
    :param y:
    :return:
    """
    if x < 50 or x > 950:
        x_temp = x + random.randrange(0, 20, 5) * random.choice([-1, 1])
    else:
        x_temp = x + random.randrange(0, 40, 5) * random.choice([-1, 1])
    if y < 50 or y > 700:
        y_temp = y + random.randrange(0, 20, 5) * random.choice([-1, 1])
    else:
        y_temp = y + random.randrange(0, 40, 5) * random.choice([-1, 1])
    if x_temp < 0 or x_temp > 1000:
        x = x
    else:
        x = x_temp
    if y_temp < 0 or y_temp > 750:
        y = y
    else:
        y = y_temp
    return x, y


def move_point_in_map(x, y, region, next=None):
    """
    OCR 得方法去移动点击小地图上点，在线程中每次加载会很慢
    :param x:
    :param y:
    :param region:
    :return:

    """
    logger.info("目的地{}:{}".format(region, (x, y)))
    if region in ["轮回司"]:
        return
    open_map()
    # xs = random.randint(490, 510)
    # ys = random.randint(340, 360)
    # client_lock_mouse_move(xs, ys)
    # 增加关闭小地图图出口的逻辑
    logger.info("开始进行地图点击")
    if next in ["狮驼岭"]:
        re = if_check_exit_box()
        if re:
            move_click_with_fight(re[0], re[1])
    # Mouse().move(600, 550)
    if region in k_maple:
        dx = k_maple[region]['dx']
        dy = k_maple[region]['dy']
        if 'start_point' in k_maple[region]:
            start = k_maple[region]['start_point'][0]
            bias_x = k_maple[region]['start_point'][1]
            bias_y = k_maple[region]['start_point'][2]
            map_xy = find_map_flag_xy()
            if map_xy is None:
                logger.warning("can't find mapxy")
                # pyautogui.press('f9')
                return
            x1, y1 = start[0], start[1]
            x2, y2 = map_xy[0] + bias_x, map_xy[1] + bias_y
            target_x = (x - x1) * dx + x2
            target_y = (y - y1) * dy + y2
        else:
            xs = random.randint(490, 510)
            ys = random.randint(340, 360)
            client_lock_mouse_move(xs, ys)
            time.sleep(1)
            (x1, y1), (x2, y2) = get_xy_in_map()
            if x1 == 0 and x2 == 0:
                return
            start = (x1, y1)
            map_xy = find_map_flag_xy()
            bias_x = x2 - map_xy[0]
            bias_y = y2 - map_xy[1]
            k_maple.update({region: {'start_point': [start, bias_x, bias_y], 'dx': dx, 'dy': dy}})
            write_to_json(k_maple, filename=constant.proxies)
            target_x = (x - x1) * dx + x2
            target_y = (y - y1) * dy + y2

    else:
        xs = random.randint(490, 510)
        ys = random.randint(340, 360)
        client_lock_mouse_move(xs, ys)
        time.sleep(1)
        logger.info("正在记录地图比例尺")
        (x1, y1), (x2, y2) = get_xy_in_map()
        if x1 == 0:
            return
        dddd = 100
        yyyy = 100
        move_with_fight(x2 + dddd, y2 + yyyy, bias=0)
        time.sleep(2)
        (x3, y3), (x4, y4) = get_xy_in_map()
        if x3 == 0:
            return
        dx = dddd / abs(x1 - x3)
        dy = -yyyy / abs(y1 - y3)
        k_maple.update({region: {'dx': dx, 'dy': dy}})
        target_x = (x - x3) * dx + x4
        target_y = (y - y3) * dy + y4
        write_to_json(k_maple, filename=constant.proxies)
        logger.info("{}地图比例尺记录结束,dx:{},dy:{}".format(region, dx, dy))
    logger.info(f"开始进行地图点击{target_x, target_x}")
    move_click_with_fight(round(target_x), round(target_y), bias=2)
    time.sleep(2)
    pyautogui.press('tab')
    return 1


def give_yabiao(name, mission_type):
    # 找到镖银

    propsxy = props.find_props(mission_type + "镖银")
    if propsxy == '':
        logger.warning("没找到镖银")
        return
    if propsxy[0] < 450:
        print('镖银已经选择好了')
    else:
        move_click_with_fight(propsxy[0], propsxy[1])
        time.sleep(random.uniform(1, 2))
        left_click()

    client_lock_mouse_move(random.randint(0, 900), random.randint(0, 300))
    give_button = props.button_to_npc()
    if give_button == '':
        logger.warning("没找到给予按钮")
        return
    move_click_with_fight(give_button[0], give_button[1])
    time.sleep(2)
    left_click()
    result = npc.find_xy_by_template(constant.gan_rao, rate=0.99)
    if result != '':
        move_click_with_fight(result[0], result[1], bias=8)


def give_task(npc_name, mission_type):
    props = Props()
    npc.close_to_npc(npc_name)
    pyautogui.press("f9")
    npc_xy = npc.find_npc_by_name(npc_name)
    if npc_xy == '':
        logger.warning("没有找到{}".format(npc_name))
        return
    move_with_fight(npc_xy[0], npc_xy[1])
    pyautogui.hotkey('alt', 'g')
    left_click()
    time.sleep(random.uniform(1, 2))
    if not props.if_props_to_npc_open():
        client_lock_mouse_move(random.randint(0, 900), random.randint(0, 300))
        right_click()

    if props.if_props_to_player_open():
        props.close_give_props_()
        return
    # 找到镖银
    propsxy = props.find_props(mission_type + "镖银")
    if propsxy == '':
        logger.warning("没找到镖银")
        return
    move_click_with_fight(propsxy[0], propsxy[1])
    time.sleep(1)
    left_click()

    client_lock_mouse_move(random.randint(0, 900), random.randint(0, 300))
    give_button = props.button_to_npc()
    if give_button == '':
        logger.warning("没找到给予按钮")
        return
    move_click_with_fight(give_button[0], give_button[1], bias=3)
    time.sleep(2)
    left_click()
    result = npc.find_xy_by_template(constant.gan_rao, rate=0.99)
    if result != '':
        move_click_with_fight(result[0], result[1], bias=8)


def move_to_target(end, name):
    # 是否停止移动
    job = IsMovedTask()
    if name == '':
        return
    # 到达目的场景，移动
    previous_city = ''
    while True:
        while fighting():
            logger.info("战斗中，等待战斗结束")
            time.sleep(1)
        now_city = get_map_name()

        if now_city == end:
            logger.info("已到达目的地，退出自动寻路")
            break

        # 有没有需要点击的东西
        if previous_city == now_city:
            re = get_chuansong_xy()
            if re is not None:
                move_click_with_fight(re[0], re[1])
                time.sleep(2)
                now_city = get_map_name()
            # 有没有干扰项目
            else:
                result = npc.find_xy_by_template(constant.gan_rao, rate=0.96)
                if result != '':
                    move_click_with_fight(result[0], result[1])
        props.close_props()

        previous_city = now_city
        path = path_search.a_star_algorithm(now_city, end)

        next_city = path[1]
        # 点击地图
        info = map_loc[now_city][next_city]
        x, y = info["XY"]
        if info["action"]["type"] == 3:
            xy_list = info["action"]["xy"]
            for xy in xy_list:
                x, y = xy
                # 增加随机，避免一直点一个点
                x, y = get_random_xy(x, y)
                move_click_with_fight(x, y, bias=10)
                click_times = random.randrange(0, 3, 1)
                while click_times > 0:
                    left_click()
                    click_times -= 1
                time.sleep(random.uniform(3, 4))
                map_name = get_map_name()
                if map_name == next_city:
                    break
            continue

        s = move_point_in_map(x, y, now_city, next=next_city)

        if s is None:
            continue

        utils_local.log_h1_start("正在前往目的地")
        skip = False
        while True:
            if fighting():
                skip = True
                break
            if not job.is_moved():
                break
        if skip:
            continue

        pyautogui.hotkey('alt', 'h')
        pyautogui.press('f9')
        if info["action"]["type"] == 0:
            x, y = info["action"]["xy"]
            # 增加随机，避免一直点一个点
            # x, y = get_random_xy(x, y)
            move_click_with_fight(x, y)
        else:
            action = info["action"]
            re = get_chuan_song_npc(now_city, next_city)
            if re is None:
                logger.info("没有找到传送NPC")
                continue
            move_click_with_fight(re[0], re[1])
            time.sleep(1)
            if "button" in action:
                re2 = get_chuansong_xy(os.path.join(constant.move_dir, action["button"]))
            else:
                re2 = get_chuansong_xy()
            if re2 is None:
                if re is not None:
                    move_click_with_fight(re[0] - 100, re[1])
                    time.sleep(3)
                    pyautogui.hotkey('alt', 'h')
                    pyautogui.press('f9')
                    time.sleep(1)
                    re = get_chuan_song_npc(now_city, next_city)
                    if re is None:
                        logger.info("没有找到传送NPC")
                        continue
                    move_click_with_fight(re[0], re[1])
                    time.sleep(1)
                    if "button" in action:
                        re2 = get_chuansong_xy(os.path.join(constant.move_dir, action["button"]))
                    else:
                        re2 = get_chuansong_xy()
                    if re2 is None:
                        logger.info("没有找到传送按钮")
                        continue
                    move_click_with_fight(re2[0], re2[1])
                    time.sleep(3)
                    continue
            move_click_with_fight(re2[0], re2[1])
        time.sleep(3)


def move_test_without_fight(end, name, mission_type):
    move_to_target(end, name)
    while True:
        while fighting():
            time.sleep(2)
            logger.info("等待战斗结束")
        # 一些前置工作
        props.close_props()
        # 是否有干扰
        result = npc.find_xy_by_template(constant.gan_rao, rate=0.99)
        if result != '':
            move_click_with_fight(result[0], result[1])
        if get_map_name() != end:
            move_to_target(end, name)
        if get_mission_type("运镖") != '' or get_misson_text() != '':
            logger.info("-------任务-----{}".format(get_mission_type("运镖")))
            if props.if_props_to_npc_open():
                give_yabiao(name, mission_type)
            else:
                give_task(name, mission_type)
        else:
            if fighting():
                continue
            else:
                add_task_nums()
                logger.info("当前没有任务")
                return


if __name__ == '__main__':
    time.sleep(2)
    from threading import Thread
    from mouse import move


    def randomMove():
        while True:
            move(random.randint(100, 700), random.randint(100, 600))


    job = Thread(target=randomMove, args=(), daemon=True)
    job.start()
    while True:
        move_point_in_map(random.randint(30, 79), random.randint(10, 190), "长寿村")
