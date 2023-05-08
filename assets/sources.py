# -*- coding: utf-8 -*-
import json
import os

from script_utils.common_utils import findfiles

basedir = os.path.abspath(os.path.dirname(__file__))

source_path = os.path.join(basedir, 'sources.json')  #
source_datas = json.load(open(source_path, 'r', encoding='utf-8'))


def get_source(source_name):
    return os.path.join(basedir, source_datas[source_name]["directory"], source_datas[source_name]["name"])


def load_json(source_name):
    path = get_source(source_name)
    json_data = json.load(open(path, 'r', encoding='utf-8'))
    return json_data


def write_json(ips, name):
    filename = get_source(name)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ips, f, indent=4, ensure_ascii=False)


def join_path(directory, name):
    return os.path.join(basedir, directory, name)


def get_file_path_by_name(directory, file_name):
    path = os.path.join(basedir, directory)
    result = findfiles(path)
    for res in result:
        if res == file_name:
            return os.path.join(path, res)
    raise KeyError


location_data = load_json("location")
proxies_data = load_json("proxies")
npc_data = load_json("npc")
props_data = load_json("props")
move_directory = os.path.join(basedir, 'move')

print(get_source("idiom_confirm"))
print(get_source("idiom_reset"))