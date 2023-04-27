import unittest
import logging
import re

from source_provider.mikanani_source_provider.provider import MikananiSourceProvider
from utils.config_reader import AbsConfigReader

logging.basicConfig(level=logging.ERROR, format='%(asctime)s-%(levelname)s: %(message)s')
class MikkananiSouirceProviderTest(unittest.TestCase):
    def setUp(self) -> None:
        reader = MemDictConfigReader({'download_param': {'tags': ["test"]}, 'downloader': 'test_downloader'})
        self.provider = MikananiSourceProvider("test", reader)
        # 一共7个记录
        self.test_file = "./test/source_provider/test_source.txt"

    def load(self, reg) -> dict:
        if reg is not None:
            pattern = re.compile(reg)
        else:
            pattern = None
        with open(self.test_file, encoding="utf-8", mode= 'r') as test_file:
            lines = test_file.readlines()
        return list(filter(lambda p: p is not None, map(lambda p: self.provider.check_anime_title(p, pattern), lines)))
    
    def test_read_config(self):
        downloader = self.provider.get_prefer_download_provider()
        self.assertEqual(downloader, 'test_downloader')
        param = self.provider.get_download_param()
        self.assertEqual({'tags': ["test"]}, param)

    def test_title_filter_full(self):
        title_dict = self.load(None)
        self.assertEqual(7, len(title_dict))

    def test_title_filter_reg_include(self):
        title_dict = self.load( ".*简.*")
        self.assertEqual(3, len(title_dict))

    def test_title_filter_reg_except(self):
        title_dict = self.load( "^((?!繁).)*$")
        self.assertEqual(4, len(title_dict))

class MemDictConfigReader(AbsConfigReader):
    def __init__(self,config: dict) -> None:
        self.config = config
    
    def save(self, new_data: dict):
        self.config = new_data

    def read(self) -> dict:
        return self.config
