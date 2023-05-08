import os
import random
import time

import cv2
import numpy as np
from PIL import ImageFont, Image, ImageDraw

from game_models.source import get_model


class ImageChar():

    def __init__(self, fontColor=(255, 255, 255),
                 size=(100, 20),
                 fontPath=r"",
                 bgColor=(0, 0, 0),
                 fontSize=30):
        self.size = size
        self.fontPath = fontPath
        self.bgColor = bgColor
        self.fontSize = fontSize
        self.fontColor = fontColor
        self.font = ImageFont.truetype(self.fontPath, self.fontSize)

        self.image = Image.new('RGB', size, bgColor)

    # def rotate(self):
    #     self.image = self.image.rotate(10, expand=0)

    def drawText(self, pos, txt, fill):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, font=self.font, fill=fill)
        del draw

    def drawTextV2(self, txt, path):
        image = Image.new('RGB', (30, 30), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, -3), txt, font=self.font, fill='white')
        w = image.rotate(random.randint(-60, 60), expand=True)
        # self.image.paste(w, box=pos)
        del draw
        w.save(path)

    def drawTextV1(self, txt):
        image = Image.new('RGB', (30, 30), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, -3), txt, font=self.font, fill='white')
        w = image.rotate(random.randint(-60, 60), expand=True)
        # self.image.paste(w, box=pos)
        del draw
        img = cv2.cvtColor(np.asarray(w), cv2.COLOR_RGB2BGR)

        return img

    def drawTextV3(self, txt):
        image = Image.new('RGB', (30, 30), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), txt, font=self.font, fill='yellow')
        del draw
        img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        return img
    #     return (random.randint(0, 255),
    #             random.randint(0, 255),
    #             random.randint(0, 255))

    def randPoint(self, num):
        (width, height) = self.size
        draw = ImageDraw.Draw(self.image)
        for i in range(0, num):
            draw.point([random.randint(0, width),
                        random.randint(0, height)], (255, 255, 255))
        # return (random.randint(0, width), random.randint(0, height)
        del draw

    # def randLine(self, num):
    #     draw = ImageDraw.Draw(self.image)
    #     for i in range(0, num):
    #         draw.line([self.randPoint(), self.randPoint()], self.randRGB())
    #     del draw

    def save(self, path):
        self.image.save(path)


def make_mock_picture(txt, save_dir, num=3):
    k1 = ImageChar(fontPath=get_model("fsong"))
    k2 = ImageChar(fontPath=get_model("simsun"))
    if save_dir is not None:
        for i in range(num):
            save_name = os.path.join(save_dir, 'mock' + "-{}.jpg".format(time.time()))
            k1.drawTextV2(txt, path=save_name)
            time.sleep(0.1)
            save_name = os.path.join(save_dir, 'mock' + "-{}.jpg".format(time.time()))
            k2.drawTextV2(txt, path=save_name)
            time.sleep(0.1)
        return None
    else:
        temp = []
        for i in range(num):
            temp.append(k1.drawTextV1(txt))
            temp.append(k2.drawTextV1(txt))
        return temp


MockWord = ImageChar(fontPath=get_model("simsun"))
if __name__ == '__main__':
    make_mock_picture("T", "TEST")




