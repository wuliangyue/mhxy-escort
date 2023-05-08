from assets.sources import get_source
from config import hover_list
from script_utils.cnOcr import cn_ocr
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterWordWhite, mutil_crop
from script_utils.matchTemplate import match_img
from src.components.window import WINDOW_ID


class Hover:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def rewardNotification(self, rate=0.9):
        screenshot = self.__screenshot()
        outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
        result = match_img(screenshot, get_source['hover_reward'], 10, 10, rate)
        if result[3] is not None:
            x, y = result[3]['rectangle'][3]
            mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
            return True
        if outs:
            for out in outs:
                text = out['text']
                xs, ys = out['position'][3]
                xs, ys = int(xs), int(ys)
                if ys > 600 or xs < 200 or xs > 850:
                    continue
                if '恭' or "喜" in text:
                    x, y = out['position'][3]
                    x, y = int(x), int(y)
                    mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                    return True
        return False

    def normalNotification(self, rate=0.9):
        screenshot = self.__screenshot()
        outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
        result = match_img(screenshot, get_source('hover_normal'), 10, 10, rate)
        if result[3] is not None:
            x, y = result[3]['rectangle'][3]
            mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
            return True
        if outs:
            for out in outs:
                text = out['text']
                xs, ys = out['position'][3]
                xs, ys = int(xs), int(ys)
                if ys > 600 or xs < 200 or xs > 850:
                    continue
                if "请选择" in text:
                    x, y = out['position'][3]
                    x, y = int(x), int(y)
                    mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                    return True
        return False

    def secondNotification(self, rate=0.9):
        screenshot = self.__screenshot()
        outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
        result = match_img(screenshot, get_source('hover_second'), 10, 10, rate, get_source('hover_second_mask'))
        if result[3] is not None:
            x, y = result[3]['rectangle'][3]
            mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
            return True
        if outs:
            for out in outs:
                text = out['text']
                xs, ys = out['position'][3]
                xs, ys = int(xs), int(ys)
                if ys > 600 or xs < 200 or xs > 850:
                    continue
                # print(text)
                if "请选择" in text:
                    x, y = out['position'][3]
                    x, y = int(x), int(y)
                    mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                    return True
        return False


hover = Hover(WINDOW_ID)
