#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from thirdparty.douyin import douyin_headers
from thirdparty.common import utils


class Download(object):
    def __init__(self, thread=5, music=True, cover=True, avatar=True, resjson=True, folderstyle=True):
        self.thread = thread
        self.music = music
        self.cover = cover
        self.avatar = avatar
        self.resjson = resjson
        self.folderstyle = folderstyle

    def progressBarDownload(self, url, filepath, desc):
        response = requests.get(url, stream=True, headers=douyin_headers)
        chunk_size = 1024  # 每次下载的数据大小
        content_size = int(response.headers['content-length'])  # 下载文件总大小
        try:
            if response.status_code == 200:  # 判断是否响应成功
                with open(filepath, 'wb') as file, tqdm(total=content_size,
                                                        unit="iB",
                                                        desc=desc,
                                                        unit_scale=True,
                                                        unit_divisor=1024,

                                                        ) as bar:  # 显示进度条
                    for data in response.iter_content(chunk_size=chunk_size):
                        size = file.write(data)
                        bar.update(size)
        except Exception as e:
            # 下载异常 删除原来下载的文件, 可能未下成功
            if os.path.exists(filepath):
                os.remove(filepath)
            print("[  错误  ]:下载出错\r")

    def awemeDownload(self, awemeDict: dict, savePath=os.getcwd()):
        if awemeDict is None:
            return
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        try:
            # 使用作品 创建时间+描述 当文件夹
            file_name = awemeDict["create_time"] + "_" + utils.replaceStr(awemeDict["desc"])
            if self.folderstyle:
                aweme_path = os.path.join(savePath, file_name)
                if not os.path.exists(aweme_path):
                    os.mkdir(aweme_path)
            else:
                aweme_path = savePath

            # 保存获取到的字典信息
            if self.resjson:
                try:
                    with open(os.path.join(aweme_path, file_name + "_result.json"), "w", encoding='utf-8') as f:
                        f.write(json.dumps(awemeDict, ensure_ascii=False, indent=2))
                        f.close()
                except Exception as e:
                    print("[  错误  ]:保存 result.json 失败... 作品名: " + file_name + "\r\n")

            desc = file_name[:30]
            # 下载  视频
            if awemeDict["awemeType"] == 0:
                video_path = os.path.join(aweme_path, file_name + "_video.mp4")

                if os.path.exists(video_path):
                    pass
                else:
                    try:
                        url = awemeDict["video"]["play_addr"]["url_list"][0]
                        if url != "":
                            self.isdwownload = False
                            self.alltask.append(
                                self.pool.submit(self.progressBarDownload, url, video_path, "[ 视频 ]:" + desc))
                    except Exception as e:
                        print("[  警告  ]:视频下载失败,请重试... 作品名: " + file_name + "\r\n")

            # 下载 图集
            if awemeDict["awemeType"] == 1:
                for ind, image in enumerate(awemeDict["images"]):
                    image_path = os.path.join(aweme_path, file_name + "_image_" + str(ind) + ".jpeg")
                    if os.path.exists(image_path):
                        pass
                    else:
                        try:
                            url = image["url_list"][0]
                            if url != "":
                                self.isdwownload = False
                                self.alltask.append(
                                    self.pool.submit(self.progressBarDownload, url, image_path, "[ 图集 ]:" + desc))
                        except Exception as e:
                            print("[  警告  ]:图片下载失败,请重试... 作品名: " + file_name + "\r\n")

            # 下载  音乐
            if self.music:
                music_name = utils.replaceStr(awemeDict["music"]["title"])
                music_path = os.path.join(aweme_path, file_name + "_music_" + music_name + ".mp3")

                if os.path.exists(music_path):
                    pass
                else:
                    try:
                        url = awemeDict["music"]["play_url"]["url_list"][0]
                        if url != "":
                            self.isdwownload = False
                            self.alltask.append(
                                self.pool.submit(self.progressBarDownload, url, music_path, "[ 原声 ]:" + desc))
                    except Exception as e:
                        print("[  警告  ]:音乐(原声)下载失败,请重试... 作品名: " + file_name + "\r\n")

            # 下载  cover
            if self.cover and awemeDict["awemeType"] == 0:
                cover_path = os.path.join(aweme_path, file_name + "_cover.jpeg")

                if os.path.exists(cover_path):
                    pass
                else:
                    try:
                        url = awemeDict["video"]["cover"]["url_list"][0]
                        if url != "":
                            self.isdwownload = False
                            self.alltask.append(
                                self.pool.submit(self.progressBarDownload, url, cover_path, "[ 封面 ]:" + desc))
                    except Exception as e:
                        print("[  警告  ]:cover下载失败,请重试... 作品名: " + file_name + "\r\n")

            # 下载  avatar
            if self.avatar:
                avatar_path = os.path.join(aweme_path, file_name + "_avatar.jpeg")

                if os.path.exists(avatar_path):
                    pass
                else:
                    try:
                        url = awemeDict["author"]["avatar"]["url_list"][0]
                        if url != "":
                            self.isdwownload = False
                            self.alltask.append(
                                self.pool.submit(self.progressBarDownload, url, avatar_path, "[ 头像 ]:" + desc))
                    except Exception as e:
                        print("[  警告  ]:avatar下载失败,请重试... 作品名: " + file_name + "\r\n")
        except Exception as e:
            print("[  错误  ]:下载作品时出错\r\n")

    def userDownload(self, awemeList: list, savePath=os.getcwd()):
        if awemeList is None:
            return
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        self.alltask = []
        self.pool = ThreadPoolExecutor(max_workers=self.thread)

        start = time.time()  # 开始时间

        for aweme in awemeList:
            self.awemeDownload(awemeDict=aweme, savePath=savePath)

        wait(self.alltask, return_when=ALL_COMPLETED)

        # 检查下载是否完成
        while True:
            print("[  提示  ]:正在检查下载是否完成...")
            self.isdwownload = True
            # 下载上一步失败的
            for aweme in awemeList:
                self.awemeDownload(awemeDict=aweme, savePath=savePath)

            wait(self.alltask, return_when=ALL_COMPLETED)

            if self.isdwownload:
                break

        end = time.time()  # 结束时间
        print('\n' + '[下载完成]:耗时: %d分钟%d秒\n' % (int((end - start) / 60), ((end - start) % 60)))  # 输出下载用时时间

