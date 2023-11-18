# This works for: https://open.ani.rip
# Function: download anime updated on ANi project
# encoding:utf-8
import logging
import traceback

import xml.etree.ElementTree as ET
import re
from typing import Union
from typing import Tuple

from source_provider import provider
from api import types
from api.values import Event, Resource
from utils import helper
from utils.config_reader import AbsConfigReader

class AniSourceProvider(provider.SourceProvider):
    '''This provider is to sync resources from ANi API: https://api.ani.rip/ani-download.xml
    For the most timely follow-up of Anime updates. 
    Downloading media in general HTTP, aria2 provider must be needed.

    Accepts 2 configs:
    Bool classification_on_directory: Choose whether the files is saved to directory according to title
    Array blacklist: Anime title that match the array will not be downloaded. NO REGEX SUPPORT.
    '''
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = False
        self.provider_type = 'ani_source_provider'
        self.rss_link = ''
        self.tmp_file_path = '/tmp/'
        self.save_path = 'ANi'
        self.provider_name = name
        self.classification_on_directory = True
        self.blacklist = []

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return None

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_download_param(self) -> dict:
        return self.config_reader.read().get('download_param', {})

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, event: Event) -> bool:
        return False

    def get_links(self, event: Event) -> list[Resource]:
        try:
            req = helper.get_request_controller()
            links_data = req.get(self.rss_link, timeout=30).content
        except Exception as err:
            logging.info('Error while fetching ANi API: %s', err)
            return []
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as cfg_file:
            cfg_file.write(links_data)
            cfg_file.close()
        blacklist = self.load_filter_config()
        return self.get_links_from_xml(tmp_xml, blacklist)

    def get_links_from_xml(self, tmp_xml, blacklist) -> list[Resource]:
        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            path = self.save_path
            ret = []
            for i in items:
                xml_title = i.find('./title').text
                item_title, item_episode, extra = self.get_anime_info(xml_title)
                url = i.find('./guid').text
                if item_title is not None:
                    logging.info('Found Anime "%s" Episode %s with info %s', item_title, item_episode, extra)
                    if not self.check_blacklist(xml_title, blacklist):
                        path_ = path + ('/{}'.format(item_title) if self.classification_on_directory else '')
                        ret.append(Resource(
                            url=url,
                            path=path_,
                            file_type=types.FILE_TYPE_VIDEO_TV,
                            link_type=self.get_link_type(),
                        ))
                else:
                    continue
            return ret
        except Exception as err:
            print(traceback.format_exc())
            logging.info('Error while parsing RSS XML: %s', err)
            return []

    def get_anime_info(self, title: str) -> Tuple[str, str, tuple]:
        '''Extract info by only REGEX, might be wrong in extreme cases.
        '''
        pattern = re.compile(r'\[ANi\] (.+?) - (\d+) \[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\.mp4')
        matches = pattern.findall(title)
        try:
            title, episode = matches[0][:2]
            extra_info = matches[0][2:]
            return title, episode, extra_info
        except Exception as e:
            logging.warning('Error while running regex on title %s: %s', title, e)
            return None, None, None

    def load_filter_config(self) -> str:
        filter = self.config_reader.read().get('blacklist', None)
        if filter is None or filter == "":
            return []
        elif isinstance(filter, list):
            return [str(item) for item in filter]
        elif isinstance(filter, str):
            return [filter]
        else:
            logging.warning('Invalid blacklist value: %s, fallback to Empty', filter)
            return []

    def check_blacklist(self, text: str, blacklist: list) -> bool:
        for item in blacklist:
            if item in text:
                logging.info('File %s will be ignored due to blacklist matched: %s', text, item)
                return True
        return False

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        cfg = self.config_reader.read()
        logging.info('ANi rss link is: %s', cfg['rss_link'])
        self.rss_link = cfg['rss_link']
        self.classification_on_directory = cfg.get('classification_on_directory', True)

