# -*- coding: utf-8 -*-

import logging
import os
import time
import sys
import re
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

from lxml import html
import requests

from utils.config_reader import AbsConfigReader
from utils import helper
from pt_provider import provider


class NexuPHPPTProvider(provider.PTProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader):
        self.name = name
        self.enable = config_reader.read().get('enable', False)
        if not self.enable:
            return

        self.main_url = config_reader.read().get('main_link', '')
        self.rss_url = config_reader.read().get('rss_link', '')
        self.download_provider = config_reader.read().get('downloader', '')
        self.keeping_time = config_reader.read().get('keep_time', 120)
        self.max_sum_size = config_reader.read().get('max_sum_size', 200.0)
        self.cost_sum_size = config_reader.read().get('cost_sum_size', 20.0)

        cookie = config_reader.read().get('cookie', '')
        self.cookie = helper.parse_cookie_string(cookie)

        self.attendance_url = os.path.join(self.main_url, 'attendance.php')

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def get_links(self) -> list:
        resp = requests.get(self.rss_url, timeout=30, cookies=self.cookie)
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as tmp_file:
            tmp_file.write(resp.text.encode('utf-8'))
            tmp_file.close()
        return self.get_links_from_xml(tmp_xml)

    def go_attendance(self) -> None:
        try:
            resp = requests.get(self.attendance_url, timeout=30, cookies=self.cookie)
            if resp.status_code != 200:
                logging.warning("Do attendance(%s) error:%s", self.name, resp.text)
        except Exception as err:
            logging.warning("Do attendance(%s) error:%s", self.name, err)

    def get_download_provider(self) -> str:
        return self.download_provider

    def get_cost_sum_size(self) -> float:
        return float(self.cost_sum_size)

    def get_max_sum_size(self) -> float:
        return float(self.max_sum_size)

    def get_keeping_time(self) -> int:
        return self.keeping_time

    def get_links_from_xml(self, tmp_xml) -> list:
        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            links = []
            for i in items:
                size = self.parse_filesize_from_title(i.find('./title').text)

                resp = requests.get(i.find('./link').text, timeout=30, cookies=self.cookie)
                # rate limited, wait some time
                if resp.status_code != 200:
                    time.sleep(180)
                    continue

                is_free = self.is_free_resource(resp.text)

                torrent_link = i.find('./enclosure').attrib['url']
                file = self.download_torrent_file(torrent_link)
                logging.info("PT provider(%s) find link:%s, size:%s, free:%s", self.name, torrent_link, size, is_free)        

                link = {'size': size, 'torrent': file, 'free': is_free}
                links.append(link)
            return links
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return []

    def download_torrent_file(self, link: str) -> str:
        tmp_file = helper.get_tmp_file_name(link) + ".torrent"
        resp = requests.get(link, timeout=30, cookies=self.cookie)
        with open(tmp_file, 'wb') as torrent_file:
            torrent_file.write(resp.content)
            torrent_file.close()
        return tmp_file

    # parse_filesize_from_title return the size in GB
    # demo: <![CDATA[ [电视剧]Secret Door 2023 S01 WEB-DL 2160p H265 AAC 2Audio-HDVWEB[1.55 GB] ]]>
    def parse_filesize_from_title(self, title: str) -> int:
        mbMatch = re.search(r"\[(\d+\.\d+)\sMB\]", title)
        if mbMatch:
            return int(mbMatch.group(1))

        gbMatch = re.search(r"\[(\d+\.\d+)\sGB\]", title)
        if gbMatch:
            return int(gbMatch.group(1))

        tbMatch = re.search(r"\[(\d+\.\d+)\sTB\]", title)
        if tbMatch:
            return int(tbMatch.group(1))

        # return max sieze and ignore this
        return sys.maxsize

    def is_free_resource(self, data: str) -> bool:
        if 'class="twoupfree"' in data:
            return True
        if 'class="free"' in data:
            return True
        return False