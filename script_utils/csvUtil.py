# -*- coding: utf-8 -*-
import os.path

import pandas as pd
from pandas import DataFrame
from datetime import datetime

from config import runs_data
from script_utils.loggerConfig import logger


def create_csv(filename, data):
    columns = [col for col in data.keys()]
    try:
        df = DataFrame(data, columns=columns)
        df.to_csv(os.path.join(runs_data, filename), mode='w', index=False, header=True, encoding='utf-8')
        logger.info(f"创建文件{filename}成功")
    except Exception as e:
        logger.error(f"创建文件错误{e}")


class CSV:
    def __init__(self, filename):
        self.path = os.path.join(runs_data, filename)
        try:
            self.df = pd.read_csv(self.path)
        except FileNotFoundError:
            logger.info(f"Not find file {self.path}")
            logger.info(f"Created file {self.path}")
            create_csv("escort.csv", {
                "name": [],
                "time": [],
                "date": []
            })
        finally:
            self.df = pd.read_csv(self.path)

    def has_name(self, key, val):
        result = self.df[key].str.contains(val)
        print(result.empty)
        if result.empty:
            return False
        return result[0]

    def add(self, data):
        if not self.has_name("name", data['name']):
            self.df = self.df.append(data, ignore_index=True)
            self.save()
        logger.info(f"{data['name']}已经存在,不需要重复添加")

    def save(self):
        self.df.to_csv(self.path, mode='w', index=False, header=True, encoding='utf-8')


class EscortCsv(CSV):
    def __init__(self, filename):
        super().__init__(filename)

    def add_task_time(self, name):
        self.df.loc[self.df['name'] == name, 'time'] = self.get_task_time(name) + 1
        self.save()

    def get_task_time(self, name):
        if not self.has_name('name', name):
            self.add({'name': name, 'time': 0, 'date': datetime.today().date().__str__()})
            self.save()
            return 0
        his_date = self.df.loc[self.df['name'] == name, 'date'][0]
        if his_date != datetime.today().date().__str__():
            self.df.loc[self.df['name'] == name, 'time'] = 0
            self.df.loc[self.df['name'] == name, 'date'] = datetime.today().date().__str__()
            self.save()
        return int(self.df.loc[self.df['name'] == name, 'time'][0])


escort_data = EscortCsv("escort.csv")
