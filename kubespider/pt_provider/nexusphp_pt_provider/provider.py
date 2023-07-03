# -*- coding: utf-8 -*-

import logging
import os
import time
import sys
import re
import xml.etree.ElementTree as ET

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
        self.cookie = config_reader.read().get('cookie', '')

        self.attendance = bool(config_reader.read().get('attendance', False))
        self.attendance_url = os.path.join(self.main_url, 'attendance.php')

        self.controller = helper.get_request_controller(self.cookie)

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def get_links(self) -> list:
        while True:
            try:
                resp = self.controller.open(self.rss_url, timeout=30).read()
                tmp_xml = helper.get_tmp_file_name('') + '.xml'
                with open(tmp_xml, 'wb') as tmp_file:
                    tmp_file.write(resp)
                    tmp_file.close()
                links = self.get_links_from_xml(tmp_xml)
                if len(links) > 0:
                    return links
                logging.info("Find no links, wait 5min and try again")
            except Exception as err:
                logging.info("Query links error:%s", err)
            finally:
                time.sleep(300)

    def go_attendance(self) -> None:
        if not self.attendance:
            return
        try:
            self.controller.open(self.attendance_url, timeout=30)
        except Exception as err:
            logging.warning("Do attendance(%s) error:%s", self.name, err)

    def get_download_provider(self) -> str:
        return self.download_provider

    def get_cost_sum_size(self) -> float:
        return float(self.cost_sum_size)

    def get_max_sum_size(self) -> float:
        return float(self.max_sum_size)

    def get_keeping_time(self) -> int:
        return self.keeping_time * 60 * 60

    def get_links_from_xml(self, tmp_xml) -> list:
        links = []
        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            logging.info("PT provider(%s) find %d items", self.name, len(items))
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return links

        for item in items:
            try:
                size = self.parse_filesize_from_title(item.find('./title').text)

                resp = self.controller.open(item.find('./link').text, timeout=30).read()
                # if too small response, it means rate limited, wait some time
                if len(resp) < 200:
                    logging.info("Not corrent data, wait 3min:%s", str(resp))
                    time.sleep(180)
                    continue

                is_free = self.is_free_resource(resp.decode('utf-8'))

                torrent_link = item.find('./enclosure').attrib['url']

                file = self.download_torrent_file(torrent_link)
                if file == "":
                    continue
                logging.info("PT provider(%s) find link:%s, size:%s, free:%s", self.name, torrent_link, size, is_free)

                link = {'size': size, 'torrent': file, 'free': is_free}
                links.append(link)
            except Exception as err:
                logging.info('Parse data error:%s', err)
                time.sleep(180)
                continue
        return links

    def download_torrent_file(self, link: str) -> str:
        tmp_file = helper.get_tmp_file_name(link) + ".torrent"
        resp = self.controller.open(link, timeout=30).read()
        with open(tmp_file, 'wb') as torrent_file:
            torrent_file.write(resp)
            torrent_file.close()
        return tmp_file


    # parse_filesize_from_title return the size in GB
    # demo: <![CDATA[ [电视剧]Secret Door 2023 S01 WEB-DL 2160p H265 AAC 2Audio-HDVWEB[1.55 GB] ]]>
    def parse_filesize_from_title(self, title: str) -> int:
        mb_match = re.search(r"\[(\d+\.\d+)\sMB\]", title)
        if mb_match:
            return float(mb_match.group(1))/1024.0

        gb_match = re.search(r"\[(\d+\.\d+)\sGB\]", title)
        if gb_match:
            return float(gb_match.group(1))

        tb_match = re.search(r"\[(\d+\.\d+)\sTB\]", title)
        if tb_match:
            return float(tb_match.group(1))*1024.0

        # return max sieze and ignore this
        return sys.maxsize

    def is_free_resource(self, data: str) -> bool:
        if "class='twoupfree'" in data:
            return True
        if "class='free'" in data:
            return True
        return False
