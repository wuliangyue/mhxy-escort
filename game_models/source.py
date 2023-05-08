# -*- coding: utf-8 -*-
import json
import os

from script_utils.common_utils import findfiles
from script_utils.loggerConfig import logger

basedir = os.path.abspath(os.path.dirname(__file__))

source_path = os.path.join(basedir, 'model.json')  #
source_datas = json.load(open(source_path, 'r', encoding='utf-8'))


def get_model(source_name, v=1):
    if v == 1:
        return os.path.join(basedir, source_datas[source_name]["directory"], source_datas[source_name]["name"])
    path = os.path.join(basedir, f"model")
    result = findfiles(path)
    for res in result:
        if res == source_name:
            return os.path.join(path, res)
    raise KeyError
