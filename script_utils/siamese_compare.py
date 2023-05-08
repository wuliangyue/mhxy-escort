import math
import os.path
import time

import cv2
import numpy
import numpy as np
import torch
from PIL import Image

from config import yolov5_repo
from game_models.source import get_model
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data
from siamese_utils.siamese import Siamese

compare_model = Siamese()

word_model = torch.hub.load(yolov5_repo, 'custom',
                            path=get_model("word"), source='local',force_reload=True)


def cv_image_to_pil(img):
    # img 是 cv2.imread()的格式
    # OpenCV图片转换为PIL image
    if not isinstance(img, numpy.ndarray):
        return Image.open(img)
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return img


def predict(template_img, img_list):
    predictions = []
    for i in img_list:
        probability = compare_siamese(template_img, i)
        predictions.append(probability)
    # print(predictions)
    logger.info(f"max predictions equal to {max(predictions)}")
    if max(predictions) < 0.5:
        return
    min_index = predictions.index(max(predictions))
    return min_index


def compare_siamese(img_1, img_2):
    img_1 = cv_image_to_pil(img_1)
    img_2 = cv_image_to_pil(img_2)
    return compare_model.detect_image(img_1, img_2).cpu().numpy()[0]


def detect_words(img, count=5):
    if not isinstance(img, numpy.ndarray):
        img = cv2.imread(img)
    result = word_model(img)
    # result.show()
    # result.save(os.path.join(constant.basedir, 'images/check_tanchuang/debug', time_str() + '.png'))
    df = result.pandas().xyxy[0]
    # df = df[df['confidence'] > 0.8]
    df.sort_values("xmin", inplace=True)
    temp = []
    for index, rows in df.iterrows():
        if count > 0:
            left_up = (int(rows['xmin']), int(rows['ymin']))
            right_down = (int(rows['xmax']), int(rows['ymax']))
            temp.append([left_up, right_down])
            count -= 1
    return temp


def clc_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_still_index(pre_list, now_list):
    store = []
    for i in range(len(now_list)):
        xmin, ymin = now_list[i][0]
        xmax, ymax = now_list[i][1]
        xcenter = (xmin + xmax) / 2
        ycenter = (ymin + ymax) / 2

        temp = []
        for k in pre_list:
            pre_xmin, pre_ymin = k[0]
            pre_xmax, pre_ymax = k[1]
            pre_xcenter = (pre_xmin + pre_xmax) / 2
            pre_ycenter = (pre_ymin + pre_ymax) / 2
            ds = clc_distance(xcenter, ycenter, pre_xcenter, pre_ycenter)
            temp.append(ds)
        re = min(temp)
        store.append(re)
    # print(store)
    return store.index(min(store))


def get_closed(point, thrid_list):
    temp = []
    for k in thrid_list:
        pre_xmin, pre_ymin = k[0]
        pre_xmax, pre_ymax = k[1]
        pre_xcenter = (pre_xmin + pre_xmax) / 2
        pre_ycenter = (pre_ymin + pre_ymax) / 2
        ds = clc_distance(point[0], point[1], pre_xcenter, pre_ycenter)
        temp.append(ds)
    index = temp.index(min(temp))
    xmin, ymin = thrid_list[index][0]
    xmax, ymax = thrid_list[index][1]
    xcenter = (xmin + xmax) / 2
    ycenter = (ymin + ymax) / 2
    return  xcenter, ycenter


def get_target(pre_img, now_img):
    pre = detect_words(pre_img)
    now = detect_words(now_img)
    still_index = (get_still_index(pre, now))

    # result = detect_words(source)
    # template_img = thresh_binary(crop(now_img, save_name=None, leftup=now[still_index][0], rihgtdown=now[still_index][1]))
    template_img = crop_image_data(now_img, left_up=now[still_index][0], right_down=now[still_index][1])

    del now[still_index]
    temp = []
    for i in range(len(now)):
        save_name = '{}.png'.format(i)
        # img = thresh_binary(crop(now_img, save_name=None, leftup=now[i][0], rihgtdown=now[i][1]))
        img = crop_image_data(now_img, left_up=now[i][0], right_down=now[i][1])
        temp.append(img)
    k = predict(template_img=template_img, img_list=temp)
    # cv2.imshow('template', template_img)
    # cv2.imshow('result', temp[k])
    # cv2.waitKey()
    if k is None:
        return 0, 0
    xmin, ymin = now[k][0]
    xmax, ymax = now[k][1]
    xcenter = (xmin + xmax) / 2
    ycenter = (ymin + ymax) / 2
    return xcenter, ycenter



if __name__ == "__main__":
    print("hello,word")
    print(detect_words(r"C:\Users\lixin10\PycharmProjects\mhxy-escort\img.png"))