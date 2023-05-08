import random

import cv2
import numpy as np

import os
import time
from numpy import mean

from assets.sources import get_source
from script_utils.cnOcr import find_text
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterWordWhite
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data, compare_image, match_img
from script_utils.siamese_compare import get_target, detect_words, compare_siamese
from siamese_utils.idiom import get_idiom
from siamese_utils.verification_code import make_mock_picture
from src.components.mouse import mouse
from src.components.window import WINDOW_ID

WORD_IMAGE = {}


def is_have_check(img=None):
    """
    :return:
    :return:
    0 移动弹窗, 1 成语弹窗

    """
    if img:
        screenshot = cv2.imread(img)
    else:
        screenshot = winShot(WINDOW_ID)
    move_corp_sceenshot = hsvFilterWordWhite(crop_image_data(screenshot, left_up=(148, 41), right_down=(701, 280)))
    result_word = find_text(move_corp_sceenshot, ["鼠标", "点选"])
    print(result_word)
    result_chengyu = match_img(screenshot, get_source("idiom_confirm"), 10, 10, 0.92)
    result_cheng_yu_reset = match_img(screenshot, get_source("idiom_reset"), 10, 10, 0.95)[3]
    if result_word is not None or result_chengyu[3] is not None or result_cheng_yu_reset is not None:
        if result_word is not None:
            leftup = (result_word[0], result_word[1]-180)
            # right = result_word[1] + 41
            # save_path = os.path.join(c.check_move_word_dir, utils_local.time_str() + '.jpg')
            # fi.crop(screenshot, save_path, leftup=leftup, rihgtdown=(leftup[0] + 350, leftup[1] + 150))
            return 0, [leftup, (leftup[0] + 350, leftup[1] + 150)]
        if result_chengyu[3] is not None:
            # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
            leftup = result_chengyu[3]['rectangle'][1]
            # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
            #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))

            # take_red_line(result_word, c.check_screenshot, '{}.png'.format(3))
            return 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]
        if result_cheng_yu_reset is not None:
            # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
            reset_xy = result_cheng_yu_reset['rectangle'][1]
            leftup = (reset_xy[0] - 105, reset_xy[1])
            # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
            #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))
            return 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]
        return
    else:
        return


def findfiles(path):
    result = []
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 循环判断每个元素是否是文件夹还是文件，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if not os.path.isdir(cur_path):
            result.append(file)
    return result


def click_move_word(rectangle):
    """
    :param rectangle: 弹窗截图的左上角和右上角，数据格式[(x1,y1),(x2,y2)]
    :return:
    """
    print(rectangle)
    mouse.move(rectangle[0][0] - 30, rectangle[0][1] - 30)
    pre_img = crop_image_data(winShot(WINDOW_ID),
                              left_up=rectangle[0], right_down=rectangle[1])
    cv2.imshow('1',pre_img)
    cv2.waitKey(0)
    time.sleep(2)
    now_img = crop_image_data(winShot(WINDOW_ID),
                              left_up=rectangle[0], right_down=rectangle[1])
    x1, y1 = get_target(pre_img, now_img)
    if x1 == 0 and y1 == 0:
        return
    # 计算最近的点
    # third_img = fi.crop_image_data(winShot(common.get_mhxy_window_by_id()),
    #                                leftup=rectangle[0], rihgtdown=rectangle[1])
    # third_list = detect_words(third_img)
    # x, y = get_closed([x1, y1], third_list)
    x, y = x1, y1
    click_x = x + rectangle[0][0]
    click_y = y + rectangle[0][1]
    mouse.move_click(click_x, click_y, bias=5)
    mouse.move(100 - random.randint(20, 70), 100 - random.randint(20, 70))
    # mouse.move(rectangle[0][0] - 30, rectangle[0][1] - 30)


def clcik_chengyu(rectangle):
    """
    :param rectangle: 图片的坐标
    :return:
    """
    # 文字识别中，所有的成语组成的list
    titles = get_title_from_shot(rectangle)
    logger.info(titles)
    chengyu_img = get_chengyu_from_shot(rectangle)

    res = []
    for t in titles:
        res.append(clc_word_value(chengyu_img, t))
    while len(res) == 0:
        logger.info("未在标题中找到四字词语，重试中......")
        titles = get_title_from_shot(rectangle)
        logger.info(titles)
        chengyu_img = get_chengyu_from_shot(rectangle)

        res = []
        for t in titles:
            res.append(clc_word_value(chengyu_img, t))
    if max(res) == 0:
        logger.info("点选字符{} 至少有一个字不在数据库中".format(titles))
        return
    template = titles[res.index(max(res))]
    logger.info(template)
    for correct_word in template:
        pre_click_img = get_chengyu_from_shot(rectangle)
        words = get_words(chengyu_img, template)
        # 特殊处理 如果有两个气字 说明荡气回肠处理有问题

        logger.info("-------{}-------------".format(words))
        if correct_word not in words:
            logger.info("文字识别不准确, 概率性点击")
            index = get_index_by_word(chengyu_img, correct_word)
            # return
        else:
            index = words.index(correct_word)
        re = detect_words(chengyu_img, count=4)
        word_rectange = np.array(re)[index]
        x = (word_rectange[0][0] + word_rectange[1][0]) / 2 + rectangle[0][0]
        y = (word_rectange[0][1] + word_rectange[1][1]) / 2 + rectangle[0][1]
        mouse.move_click(x, y)
        mouse.move(random.uniform(10, 700), random.uniform(10, 100))
        chengyu_img = get_chengyu_from_shot(rectangle)

        # 点击后图片未变化，表示点击了重复数字
        if is_has_two(correct_word, template):
            logger.info("存在重复数字:{}".format(correct_word))
            rate = compare_image(pre_click_img, chengyu_img, channel_axis=True)
            if rate > 0.99:
                logger.info('点击前后图片无变化')
                words = list(words)
                words[index] = "0"
                words = ''.join(words)
                if correct_word not in words:
                    mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                    return "rest"
                index = words.index(correct_word)
                re = detect_words(chengyu_img, count=4)
                word_rectange = np.array(re)[index]
                x = (word_rectange[0][0] + word_rectange[1][0]) / 2 + rectangle[0][0]
                y = (word_rectange[0][1] + word_rectange[1][1]) / 2 + rectangle[0][1]
                mouse.move_click(x, y)
                mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                chengyu_img = get_chengyu_from_shot(rectangle)

    confirm_x = rectangle[0][0] + 170 + 25
    confirm_y = rectangle[0][1] + 170 - 10
    mouse.move_click(confirm_x, confirm_y)
    mouse.move(random.uniform(10, 700), random.uniform(10, 100))


def click_check(retry=5, sleep_time=30):
    """
    :param retry: 点击弹窗的次数
    :param sleep_time: 遇到弹窗校验的时间间隔
    :return: 是否遭遇弹窗
    """
    # 暂停
    flag = False
    check_result = is_have_check()
    retry_times = retry
    cheng_yu_retry = 3
    if check_result is not None:
        have_check = True
        tan_type = check_result[0]
        rectangle = check_result[1]
    else:
        have_check = False
        tan_type = None
        rectangle = None
    while have_check:
        # 点击移动弹窗
        if tan_type == 0 and retry_times >= 0:
            logger.info("开始点击移动弹窗,剩余次数{}".format(retry_times))
            flag = True
            click_move_word(rectangle)
            retry_times = retry_times - 1
            time.sleep(4)
            img = crop_image_data(winShot(WINDOW_ID),
                                  left_up=rectangle[0], right_down=rectangle[1])
            words = detect_words(img)
            if len(words) >= 4:
                have_check = True
                check_result = is_have_check()
                if check_result is not None:
                    tan_type = check_result[0]
                    rectangle = check_result[1]
            else:
                have_check = False
            continue
        elif tan_type == 0 and retry_times < 0:
            logger.warning(f"出现移动弹窗，请尽快处理,已经尝试{retry}次点击")
            time.sleep(60)
        # 点击成语弹窗
        if tan_type == 1:
            # send("{}出现成语弹窗，请尽快处理".format(common.title))
            if flag and cheng_yu_retry <= 0:
                logger.warning("弹窗成语识别/点击失败,请尽快处理")
            else:
                flag = True
                result = clcik_chengyu(rectangle)
                if result != "rest":
                    cheng_yu_retry = cheng_yu_retry - 1
                time.sleep(3)
                check_result = is_have_check()
                if check_result is not None:
                    reset_x = rectangle[0][0] + 170 + 25 + 100
                    reset_y = rectangle[0][1] + 170 - 10
                    mouse.move_click(reset_x, reset_y)
                    mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                    have_check = True
                else:
                    have_check = False
                continue
        # 继续循环
        time.sleep(sleep_time)
        # check_result = is_have_check()
    if flag:
        logger.info("弹窗消失,弹窗类型{}".format(tan_type))
    return flag


def load_word_img_to_memory(words):
    """

    :param words:
    :return:
    """
    logger.info("生成加载文字图片,使用mock方式")
    for word in words:
        WORD_IMAGE[word] = make_mock_picture(word, save_dir=None, num=3)


def clc_word_value(img, words):
    """
    计算一个词语 与这个图片的关联性
    :param img:
    :param words:
    :return:
    """
    load_word_img_to_memory(words)

    templates = detect_words(img, count=4)
    result = []
    for k in range(len(templates)):
        template_img = crop_image_data(img, left_up=templates[k][0], right_down=templates[k][1])
        temp = []
        for word in words:
            # word_dir = os.path.join(dir_path, word)
            word_img_list = WORD_IMAGE[word]
            similarity = 0
            for s in word_img_list:
                clc_similarity = compare_siamese(template_img, s)
                if clc_similarity > similarity:
                    similarity = clc_similarity
            # print("第{}图,在--{}--上,最大的相似度为:{}".format(k,word,similarity))
            temp.append(similarity)
        result.append(max(temp))
    return mean(result)


def get_word(wrod_img, words, num):
    temp = []
    for word in words:
        # word_dir = os.path.join(dir_path, word)
        word_img_list = WORD_IMAGE[word]
        similarity = 0
        for img in word_img_list:
            clc_similarity = compare_siamese(wrod_img, img)
            if clc_similarity > similarity:
                similarity = clc_similarity
        logger.info("第{}张图在--{}--上,相似度为:{}".format(num, word, similarity))
        temp.append(similarity)
    index = temp.index(max(temp))
    return words[index]


def get_index_by_word(crops_img, word):
    temp = []
    templates = detect_words(crops_img, count=4)
    for k in range(len(templates)):
        template_img = crop_image_data(crops_img, left_up=templates[k][0], right_down=templates[k][1])
        word_img_list = WORD_IMAGE[word]
        similarity = 0
        for img in word_img_list:
            clc_similarity = compare_siamese(template_img, img)
            if clc_similarity > similarity:
                similarity = clc_similarity
        logger.info("第{}张图在--{}--上,相似度为:{}".format(k, word, similarity))
        temp.append(similarity)
    index = temp.index(max(temp))
    return index


def get_words(crops_img, words):
    result = ''
    templates = detect_words(crops_img, count=4)
    for k in range(len(templates)):
        template_img = crop_image_data(crops_img, left_up=templates[k][0], right_down=templates[k][1])
        word = get_word(template_img, words, num=k)
        result += word
    return result


def get_title_from_shot(rectangle):
    left_up = rectangle[0]
    right_down = rectangle[1]
    crop_img = crop_image_data(winShot(WINDOW_ID), left_up=(left_up[0], left_up[1] - 120),
                               right_down=(right_down[0] + 180, right_down[1] - 102))
    return get_idiom(crop_img)


def get_chengyu_from_shot(rectangle):
    return crop_image_data(winShot(WINDOW_ID), left_up=rectangle[0],
                           right_down=rectangle[1])


def is_has_two(word, words):
    count = 0
    for i in words:
        if i == word:
            count += 1
    if count == 1:
        return False
    else:
        return True


if __name__ == '__main__':
    click_check(20)
