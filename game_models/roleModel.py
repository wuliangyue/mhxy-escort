# -*- coding: gbk -*-
import torch

from config import yolov5_repo
from game_models.source import get_model
from script_utils.loggerConfig import logger

model = torch.hub.load(yolov5_repo, 'custom',
                       path=get_model('role'),
                       source='local')  # local model


def get_role_center(img):
    logger.info('��ʼ�������ͼ���ͷ������')
    results = model(img)
    df = results.pandas().xyxy[0]
    if len(df) == 0:
        logger.info('δ�ҵ�ͼ���е�ͷ��')
        return 45, 70
    else:
        xmin = df.loc[0]["xmin"]
        ymin = df.loc[0]["ymin"]
        xmax = df.loc[0]["xmax"]
        ymax = df.loc[0]["ymax"]

        xcenter = (xmin + xmax) / 2
        ycenter = (ymin + ymax) / 2
        return xcenter, ycenter
