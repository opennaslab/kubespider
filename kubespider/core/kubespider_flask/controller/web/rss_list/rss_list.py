# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: rss_list.py
@time: 2023/4/11 22:35
"""
import json
import os.path
import sys
import uuid

from flask import Blueprint, request

rss_list_bp = Blueprint("rss_list", __name__, url_prefix="/rss")
general_rss_file = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), ".config/general_rss.json")

@rss_list_bp.route("/list", methods=["POST"])
def rss_list():
    rss_name = request.json.get("rss_name")
    rss_type = request.json.get("type")
    state = request.json.get("state")
    rss_list = []
    with open(general_rss_file, "r") as file:
        rss_info = json.loads(file.read())

    filter_flag = 0

    if rss_name:
        filter_flag += 1

    if rss_type:
        filter_flag += 2

    if state:
        filter_flag += 4


    for rss in rss_info.get("rss"):
        if filter_flag == 0:
            rss_list.append(rss)
        if filter_flag == 1 and rss.get("rss_name") == rss_name:
            rss_list.append(rss)
            continue
        if filter_flag == 2 and rss.get("type") == rss_type:
            rss_list.append(rss)
            continue
        if filter_flag == 4 and rss.get("state") == state:
            rss_list.append(rss)
            continue
        if filter_flag == 3 and rss.get("rss_name") == rss_name and rss.get("type") == rss_type:
            rss_list.append(rss)
            continue
        if filter_flag == 5 and rss.get("rss_name") == rss_name and rss.get("state") == state:
            rss_list.append(rss)
            continue
        if filter_flag == 6 and rss.get("type") == rss_type and rss.get("state") == state:
            rss_list.append(rss)
            continue
        if filter_flag == 6 and rss.get("type") == rss_type and rss.get("state") == state and rss.get("rss_name") == rss_name:
            rss_list.append(rss)
            continue
    return {"success": True, "data": rss_list}


@rss_list_bp.route("/edit", methods=["POST"])
def rss_edit():
    data = request.json
    data.pop("index")
    edit_index = 0
    with open(general_rss_file, "r") as file:
        rss_list = json.loads(file.read()).get("rss")
        for index, rss in enumerate(rss_list):
            if rss.get("id") == data.get("id"):
                edit_index = index
                break
        rss_list[edit_index] = {**data}
    with open(general_rss_file, "w") as file:
        json.dump({"rss": rss_list}, file, indent=4, ensure_ascii=False)

    return {"success": True}


if __name__ == '__main__':
    a = {
        "rss": [
            {
                "id": uuid.uuid1().__str__(),
                "rss_name": "test",
                "rss_url": "test",
                "type": "电影",
                "state": "open",
                "decs": "decs",
                "exec_time": "8h",
                "now_time": "0h",
            }
        ]
    }

    with open('D:\Python_Project\kubespider\github\kubespider\.config\general_rss.json', "w") as file:
        json.dump(a, file, indent=4, ensure_ascii=False)
    pass


