import re

from rapidfuzz import fuzz, process
from cnocr import CnOcr

cn_ocr = CnOcr()


def get_chinese_text(text):
    rex = r'[\u4e00-\u9fa5]*'
    res = re.findall(rex, text)
    temp = ''
    for s in res:
        if s != "":
            temp += s
    return temp


def get_number(text):
    return re.findall('\d+', text)


def get_closed_string(name: str, name_list: list) -> str:
    result = process.extractOne(name, name_list)
    return result[0]


def find_text(source, txts, debug=True):
    """
    :param txts:
    :param debug: Debug
    :param source: 你想要搜索的图片
    :return: 文字的坐标 或者如果没找到 返回为None
    """
    result = cn_ocr.ocr(source)
    if debug:
        print("ocr识别文字结果:{}".format(result))
    if not result:
        return
    for res in result:
        split_txt = res['text']
        for word in txts:
            if word in split_txt:
                x = res['position'][0][0]
                y = res['position'][0][1]
                return x, y
    return


