# -*- coding: utf-8 -*-

import logging
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
        self.main_url = config_reader.read().get('main_link', '')
        self.rss_url = config_reader.read().get('rss_link', '')
        self.attendance_url = config_reader.read().get('attendance_link', '')
        self.download_provider = config_reader.read().get('downloader', '')

        cookie = config_reader.read().get('cookie', '')
        self.cookie = helper.parse_cookie_string(cookie)

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

    def get_links_from_xml(self, tmp_xml) -> list:
        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            links = []
            for i in items:
                text = i.find('./link').text
                link = self.parse_link_info(text)
                if link is not None:
                    links.append(link)
            return links
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return []

    def parse_link_info(self, link: str) -> dict:
        resp = requests.get(link, timeout=30, cookies=self.cookie)
        size = 0.0
        try:
            tree = html.fromstring(resp.text)
            item = tree.xpath("//td[b='大小：']/text()[1]")[0]
            size = self.parse_link_size(item)
        except Exception as err:
            logging.info('parse link info error:%s', err)
            return None

        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        torrent_link = self.main_url + "/download.php?id="+query_params['id'][0]

        self.go_thanks(query_params['id'][0])

        file = self.download_torrent_file(torrent_link)
        logging.info("PT provider(%s) find link:%s, size:%s", self.name, torrent_link, size)
        return {'size': size, 'torrent': file}

    def download_torrent_file(self, link: str) -> str:
        tmp_file = helper.get_tmp_file_name(link)
        resp = requests.get(link, timeout=30, cookies=self.cookie)
        with open(tmp_file, 'wb') as torrent_file:
            torrent_file.write(resp.content)
            torrent_file.close()
        return tmp_file

    def parse_link_size(self, info: str) -> float:
        if 'GB' in info:
            size_data = info.split('GB')
            if len(size_data) != 2:
                return 0.0
            return float(size_data[0])
        if 'MB' in info:
            size_data = info.split('MB')
            if len(size_data) != 2:
                return 0.0
            return float(size_data[0])/1024.0
        if 'TB' in info:
            size_data = info.split('TB')
            if len(size_data) != 2:
                return 0.0
            return float(size_data[0])*1024.0
        return 0.0

    def go_thanks(self, download_id: str) -> None:
        thank_url = self.main_url + "/thanks.php"
        data = "id="+download_id
        try:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            resp = requests.post(thank_url, data=data, cookies=self.cookie, headers=headers, timeout=30)
            if resp.status_code != 200:
                logging.warning("Do thanks(%s) error:%s", self.name, resp.text)
        except Exception as err:
            logging.error("Do thanks(%s) error:%s", self.name, err)
