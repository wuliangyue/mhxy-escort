# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import shutil
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow import keras

from config import train_dir, validation_dir
from game_models.source import get_model
from script_utils.loggerConfig import logger

AUTOTUNE = tf.data.experimental.AUTOTUNE

model = None

IMG_HEIGHT = 140
IMG_WIDTH = 90


def model_load():
    logger.info('模型读取')
    logger.info('模型路径为:{}'.format(get_model('four_people')))
    global model
    model = keras.models.load_model(get_model('four_people'))
    model.summary()


def model_predict(imgs, use_paths=True):
    logger.info('模型预测')
    global model
    if use_paths:
        imgs = [load_and_preprocess_image(path) for path in imgs]
        # print(imgs)
    imgs = tf.convert_to_tensor(imgs)
    predictions = model.predict(imgs)
    predictions = [row[0] for row in predictions]
    logger.info(predictions)
    min_index = predictions.index(min(predictions))
    logger.info(f' 预测结果为 第 > {min_index + 1} < 张图片')
    return min_index


def model_predict_tool(img):
    logger.info('模型预测')
    img = [load_and_preprocess_image(img)]
    imgs = tf.convert_to_tensor(img)
    predictions = model.predict(imgs)
    predictions = [row[0] for row in predictions]
    return predictions[0]


def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])
    image /= 255.0  # normalize to [0,1] range
    return image


def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)


if __name__ == '__main__':
    model_load()
    print(model_predict_tool(r"C:\Users\lixin10\PycharmProjects\mhxy-escort\img.png"))
