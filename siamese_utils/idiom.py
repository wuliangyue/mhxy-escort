# -*- coding: utf-8 -*-
import os
import cv2
import jieba
import numpy

from game_models.source import get_model
from script_utils.cnOcr import cn_ocr

jieba.load_userdict(get_model("words.txt", 2))


def get_file_content(filePath):
    with open(filePath, "rb") as fp:
        return fp.read()


def get_idiom(img):
    # 调用通用文字识别（标准版）
    if not isinstance(img, numpy.ndarray):
        img = cv2.imread(img)
    temp = []
    outs = cn_ocr.ocr(img)
    correct_s = ""
    for out in outs:
        correct_s += out['text']
    # 对纠错后文本进行分词
    cut_res = jieba.cut(correct_s, cut_all=True)
    for cut in cut_res:
        if len(cut) == 4:
            if cut not in temp:
                temp.append(cut)

    if "挥金如士" in correct_s:
        temp.append("挥金如土")
    if "全篇文章" in temp:
        temp.append("断章取义")
    if "虚度光阴" in temp:
        temp.append("蹉跎岁月")
    return temp
