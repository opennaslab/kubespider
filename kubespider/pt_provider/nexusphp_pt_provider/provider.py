# -*- coding: utf-8 -*-
import copy
import io
import logging
import re
from collections import namedtuple
from urllib.parse import urljoin
import requests
from lxml import etree

from api.types import LINK_TYPE_TORRENT, FILE_TYPE_PT
from api.values import Task, Resource
from pt_provider.provider import Torrent
from utils.config_reader import AbsConfigReader
from utils import helper
from pt_provider import provider
from utils.helper import retry

national_named_tuple = namedtuple(
    "national",
    ["english", "simplified_chinese", "traditional_chinese"]
)
torrent_size_translater = {
    "B": lambda x: round(float(x) / 1024 / 1024 / 1024, 2),
    "KB": lambda x: round(float(x) / 1024 / 1024, 2),
    "MB": lambda x: round(float(x) / 1024, 2),
    "GB": lambda x: round(float(x), 2),
    "TB": lambda x: round(float(x) * 1024, 2),
    "PB": lambda x: round(float(x) * 1024 * 1024, 2),
}


class National:
    """
    multi-language configuration
    Nexus supports multi-language configurations, and when extracting information from it, precise text matching is
    unavoidable. Therefore, it is necessary to configure the correspondence between different language attributes.
    Some attributes are extracted from label properties such as images, and these label properties are consistent,
    all in English expression. The rest need to be manually matched.
    """
    # user detail
    join_date = national_named_tuple("Join date", "加入日期", "加入日期")  # type:str
    last_seen = national_named_tuple("Last seen", "最近动向", "最近動向")  # type:str
    ip_addr = national_named_tuple("IP Address", "当前IP", "目前IP")  # type:str
    bt_client = national_named_tuple("", "BT客户端", "BT用戶端")  # type:str
    transfers = national_named_tuple("Transfers", "传输", "傳送")  # type:str
    uploaded = national_named_tuple("Uploaded", "上传量", "上傳量")  # type:str
    downloaded = national_named_tuple("Downloaded", "下载量", "下載量")  # type:str
    torrenting_time = national_named_tuple("Torrenting Time", "BT时间", "BT時間")  # type:str
    seeding_time = national_named_tuple("Seeding Time", "做种时间", "做種時間")  # type:str
    leeching_time = national_named_tuple("Leeching Time", "下载时间", "下載時間")  # type:str
    level = national_named_tuple("Class", "等级", "等級")  # type:str
    karma_points = national_named_tuple("Karma Points", "魔力值", "魔力值")  # type:str
    hit_and_run = national_named_tuple("H&R", "H&R", "H&R")  # type:str
    # torrents
    # These multi-language correspondences are taken from the "alt" attributes of images, and the correspondences
    # between different languages for these attributes are the same.
    size = national_named_tuple("size", "size", "size")  # type:str
    torrent_count = national_named_tuple("seeders", "seeders", "seeders")  # type:str
    download_count = national_named_tuple("leechers", "leechers", "leechers")  # type:str
    comment_count = national_named_tuple("comments", "comments", "comments")  # type:str
    complete_count = national_named_tuple("snatched", "snatched", "snatched")  # type:str
    alive_time = national_named_tuple("time", "time", "time")  # type:str
    # If these attributes do not have corresponding relationships, they need to be manually filled in.
    title = national_named_tuple("", "标题", "標題")  # type:str
    upload = national_named_tuple("", "上传", "上傳")  # type:str
    download = national_named_tuple("", "下载", "下載")  # type:str
    transfers_rate = national_named_tuple("", "分享率", "分享率")  # type:str
    download_progress = national_named_tuple("", "进度", "進度")  # type:str
    publisher = national_named_tuple("", "发布者", "發佈者")  # type:str
    # Promotion
    """
    Free: During the promotional period, download quantities for this resource are not counted, while upload quantities 
          are calculated as usual.
    2X: During the promotional period, download quantities for this resource are calculated as usual, while upload 
        quantities are calculated at twice the rate.
    2XFree: During the promotional period, download quantities for this resource are not counted, while upload 
            quantities are calculated at twice the rate.
    2X50%: During the promotional period, download quantities for this resource are calculated at 50%, while upload 
           quantities are calculated at twice the rate.
    50%: During the promotional period, download quantities for this resource are calculated at 50%, while upload 
         quantities are calculated as usual.
    30%：During the promotional period, download quantities for this resource are calculated at 30%, while upload 
         quantities are calculated as usual.
    H&R: For torrents with the H&R (Hit and Run) flag, within 60 days, you must seed for a total of 336 hours or achieve
         a share ratio of 1. Failure to meet these requirements will result in 1 H&R record.
    """
    double_free = national_named_tuple("2X Free", "2X Free", "2X Free")  # type:str
    double = national_named_tuple("2X", "2X", "2X")  # type:str
    free = national_named_tuple("Free", "Free", "Free")  # type:str
    fifty_percent = national_named_tuple("50%", "50%", "50%")  # type:str
    double_fifty_percent = national_named_tuple("2X 50%", "2X 50%", "2X 50%")  # type:str
    thirty_percent = national_named_tuple("30%", "30%", "30%")  # type:str

    def is_promotion(self, attr) -> bool:
        if attr in [self.double_free, self.double, self.double_fifty_percent, self.fifty_percent, self.free,
                    self.thirty_percent]:
            return True
        return False

    def is_img_alt_attribute(self, attr) -> bool:
        if attr in [self.size, self.torrent_count, self.download_count, self.complete_count, self.comment_count,
                    self.alive_time]:
            return True
        return False

    def __init__(self, language: str):
        self._lg = language

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if isinstance(attr, national_named_tuple):
            return getattr(attr, self._lg)
        return attr


class NexusTorrent(Torrent):

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.title = kwargs.get("title", None)
        self.describe = kwargs.get("describe", None)
        self.size = kwargs.get("size", None)
        self.torrent_content = None  # type: [io.BytesIO,None]
        self.promotion = kwargs.get("promotion", set())
        self.upload_size = kwargs.get("upload_size", None)
        self.download_size = kwargs.get("download_size", None)
        self.seeding_count = kwargs.get("seeding_count", None)
        self.downloading_count = kwargs.get("downloading_count", None)
        self.complete_count = kwargs.get("complete_count", None)
        self.transfers_rate = kwargs.get("transfers_rate", None)
        self.alive_time = kwargs.get("alive_time", None)
        self.download_progress = kwargs.get("download_progress", None)

        # TODO
        self.free_time = None
        self.hit_and_run = None

    @property
    def downloading(self) -> [bool, None]:
        if self.download_size is None or self.size is None:
            return None
        if self.size > self.download_size:
            return True
        return False

    @property
    def download_complete(self) -> [bool, None]:
        if self.download_size is None or self.size is None:
            return None
        if self.download_size >= self.size:
            return True
        return False

    def __add__(self, other) -> Torrent:
        if not isinstance(other, NexusTorrent):
            raise Exception("Unsupported torrent type")
        if self.id != other.id:
            raise ValueError("Addition not supported different torrent id")
        self.title = self.title or other.title
        self.describe = self.describe or other.describe
        self.size = self.size or other.size
        self.promotion = self.promotion or other.promotion
        self.upload_size = self.upload_size or other.upload_size
        self.download_size = self.download_size or other.download_size
        self.seeding_count = self.seeding_count or other.seeding_count
        self.downloading_count = self.downloading_count or other.downloading_count
        self.complete_count = self.complete_count or other.complete_count
        self.transfers_rate = self.transfers_rate or other.transfers_rate
        self.alive_time = self.alive_time or other.alive_time
        self.download_progress = self.download_progress or other.download_progress
        self.free_time = self.free_time or other.free_time
        self.hit_and_run = self.hit_and_run or other.hit_and_run
        return self

    @classmethod
    def merge_torrents(cls, torrents: list[Torrent]) -> list[Torrent]:
        torrents_map = {}
        for torrent in torrents:
            if not torrent.id:
                continue
            if torrent.id not in torrents_map:
                torrents_map.setdefault(torrent.id, torrent)
            else:
                torrents_map[torrent.id] += torrent
        return list(torrents_map.values())

    @property
    def data(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "describe": self.describe,
            "size": self.size,
            "promotion": list(self.promotion),
            "upload_size": self.upload_size,
            "download_size": self.download_size,
            "seeding_count": self.seeding_count,
            "downloading_count": self.downloading_count,
            "complete_count": self.complete_count,
            "transfers_rate": self.transfers_rate,
            "alive_time": self.alive_time,
            "download_progress": self.download_progress,
            "free_time": self.free_time,
            "hit_and_run": self.hit_and_run,
            "downloading": self.downloading,
            "download_complete": self.download_complete,
        }

    def to_download_task(self) -> Task:
        return Task()

    def to_download_resource(self, torrent_content: io.BytesIO, download_path: str) -> Resource:
        return Resource(
            url="",
            torrent_content=torrent_content,
            path=download_path,
            link_type=LINK_TYPE_TORRENT,
            file_type=FILE_TYPE_PT,
        )

    def __repr__(self) -> str:
        return f"<NexusTorrent {str(self.data)}>"

    @classmethod
    def init_torrent_from_xml(cls, element):
        """get title,describe,size,torrent id from xml"""
        enclosure = element.find('./enclosure').attrib
        title = element.find('./title').text
        size = torrent_size_translater.get("B", lambda x: None)(enclosure.get("length", 0))
        if not size:
            mb_match = re.search(r"\[(\d+\.\d+)\sMB\]", title)
            if mb_match:
                size = torrent_size_translater.get("MB", lambda x: None)(mb_match.group(1))
            gb_match = re.search(r"\[(\d+\.\d+)\sGB\]", title)
            if gb_match:
                size = torrent_size_translater.get("GB", lambda x: None)(mb_match.group(1))
            tb_match = re.search(r"\[(\d+\.\d+)\sTB\]", title)
            if tb_match:
                size = torrent_size_translater.get("TB", lambda x: None)(mb_match.group(1))
        detail_link = element.find('./link').text
        download_link = enclosure.get("url", "")
        match = re.findall(r'id=(\d*)', detail_link)
        torrent_id = match[0] if match else None
        if not torrent_id:
            match = re.findall(r'id=(\d*)', download_link)
            torrent_id = match[0] if match else None
        torrent = cls(id=torrent_id, title=title, size=size)
        return torrent

    @classmethod
    def init_torrent_from_html(cls, element, columns, language: National) -> Torrent:
        """
        get title,describe,promotion,torrent id,size,upload_size,download_size,seeding_count,downloading_count,
        complete_count,transfers_rate,alive_time,download_progress from html
        """
        tds = element.xpath("./td")
        if len(tds) != len(columns):
            logging.warning(
                "[NexusTorrent]The length of the element:%s does not match the length of the columns:%s",
                len(tds), len(columns)
            )
            return cls(id=None)
        torrent_id = None
        title = None
        describe = None
        promotion = None
        size = None
        upload_size = None
        download_size = None
        seeding_count = None
        downloading_count = None
        complete_count = None
        transfers_rate = None
        alive_time = None
        download_progress = None
        for index, name in enumerate(columns):
            if name == language.title:
                title = tds[index].xpath(".//a/@title")
                title = title[0] if title else None
                children_td = tds[index].xpath(".//td")
                if children_td:
                    describe = [text.strip() for text in tds[index].xpath(".//td/text()") if text.strip()]
                else:
                    describe = [text.strip() for text in tds[index].xpath(".//text()") if text.strip()]
                describe = describe[-1] if describe else ""
                alts = tds[index].xpath(".//img/@alt")
                promotion = set()
                for alt in alts:
                    if language.is_promotion(alt):
                        promotion.add(alt)
                for href in tds[index].xpath(".//a/@href"):
                    match = re.findall(r"details\.php\?id=(\d*)", href)
                    if match:
                        torrent_id = match[0]
            elif name == language.size:
                match = tds[index].xpath("./text()")
                if len(match) == 2:
                    size = torrent_size_translater.get(match[1])(match[0])
            elif name == language.upload:
                match = tds[index].xpath("./text()")
                if len(match) == 2:
                    upload_size = torrent_size_translater.get(match[1])(match[0])
            elif name == language.download:
                match = tds[index].xpath("./text()")
                if len(match) == 2:
                    download_size = torrent_size_translater.get(match[1])(match[0])
            elif name == language.torrent_count:
                match = tds[index].xpath(".//text()")
                seeding_count = int(match[0]) if match else None
            elif name == language.download_count:
                match = tds[index].xpath(".//text()")
                downloading_count = int(match[0]) if match else None
            elif name == language.complete_count:
                match = tds[index].xpath(".//text()")
                complete_count = int(match[0]) if match else None
            elif name == language.transfers_rate:
                match = tds[index].xpath(".//text()")
                try:
                    transfers_rate = round(float(match[0]), 3) if match else None
                except:
                    transfers_rate = None
            elif name == language.alive_time:
                match = tds[index].xpath(".//span/@title")
                alive_time = match[0] if match else None
            elif name == language.download_progress:
                match = tds[index].xpath(".//text()")
                download_progress = match[0] if match else None
        return cls(
            id=torrent_id,
            title=title,
            describe=describe,
            promotion=promotion,
            size=size,
            upload_size=upload_size,
            download_size=download_size,
            seeding_count=seeding_count,
            downloading_count=downloading_count,
            complete_count=complete_count,
            transfers_rate=transfers_rate,
            alive_time=alive_time,
            download_progress=download_progress,
        )

    def update_property(self, content: str, language: National) -> None:
        """Obtain some missing property from the detail page"""
        # TODO  Implement more
        promotion_css_map = {
            "class='twoupfree'": language.double_free,
            "class='free'": language.free,
            "class='halfdown'": language.fifty_percent,
            "class='thirtypercent'": language.thirty_percent
        }
        for key, value in promotion_css_map.items():
            if key in content:
                self.promotion.add(value)

    @property
    def is_effective_torrent(self) -> bool:
        """Determine whether the current torrent is a valid torrent (whether there are missing attributes)"""
        return all([self.id, self.size, self.alive_time])

    @property
    def worthless_upload_torrent(self) -> bool:
        """Seeds without upload value: Downloads are already completed, the free period has expired,
         and there is no upload volume."""
        if not self.is_free and not self.upload_size and self.download_complete:
            return True
        return False

    @property
    def need_remove(self) -> bool:
        """Seeds that need to be deleted: Not completed in downloading and have expired."""
        if self.worthless_upload_torrent or (not self.is_free and self.downloading):
            return True
        return False

    @property
    def already_download(self) -> bool:
        return self.downloading or self.download_complete

    @property
    def seeding_time(self):
        # TODO
        return

    @property
    def is_free(self) -> bool:
        if "2X" in self.promotion or "2X Free" in self.promotion:
            return True
        return False

    @property
    def alive(self) -> float:
        # TODO
        return 0

    def a(self, t0=4, n0=7):
        """
        A value is the algorithm key value that Nexus uses to calculate upload magic, and a larger value is better.
        ti: The lifetime of the i-th seed, which is the time elapsed since the seed was published until now, is measured in weeks.
        t0: Parameter t0 is equal to 4.
        si: The size of the i-th seed is measured in gigabytes (GB).
        ni: The current number of seeders for the i-th seed.
        n0: Parameter n0 is equal to 7.
        """
        ti = self.alive
        si = self.size
        ni = self.seeding_count
        if all([ti, t0, n0, ni, si]):
            #          Seed Lifetime Impact * Seed Size * Current Seeder Count Impact
            return (1 - 10 ** (-1 / t0 * ti)) * si * (1 + 1.414 * 10 ** (-1 / (n0 - 1) * (ni - 1)))
        return 0

    def d(self):
        """
        The download value (earning upload) of the seed, the larger, the better.
        """
        # TODO
        return 0


class NexusHttpClient:
    def __init__(self, host, reqeust_handler):
        self.host = host
        self.request_handler = reqeust_handler or requests.Session()

    @retry(delay=180)
    def login(self, username, password):
        # TODO
        url = urljoin(self.host, f"/login.php")
        dom = etree.HTML(self.request_handler.get(url).content)
        verification_img = dom.xpath("//img/@src")
        if verification_img:
            verification_code = self.get_verification_code(verification_img[0])
        return

    @retry(delay=180)
    def get_verification_code(self, url):
        url = urljoin(self.host, url)
        return self.request_handler.get(url)

    @retry(delay=180)
    def get(self, url, **kwargs):
        url = urljoin(self.host, url)
        return self.request_handler.get(url, **kwargs)

    @retry(delay=180)
    def get_index(self):
        return self.request_handler.get(self.host)

    @retry(delay=180)
    def get_user_detail(self, user_id):
        url = urljoin(self.host, f"userdetails.php?id={user_id}")
        return self.request_handler.get(url)

    @retry(delay=180)
    def attendance(self):
        url = urljoin(self.host, "attendance.php")
        return self.request_handler.get(url)

    @retry(delay=180)
    def rss_basket(self):
        url = urljoin(self.host, "myrss.php")
        return self.request_handler.get(url)

    @retry(delay=180)
    def rss_scribe(self):
        url = urljoin(self.host, "getrss.php")
        return self.request_handler.get(url)

    @retry(delay=180)
    def get_user_torrent_list(self, user_id, torrent_type):
        url = urljoin(self.host, f"getusertorrentlistajax.php?userid={user_id}&type={torrent_type}")
        return self.request_handler.get(url)

    @retry(delay=180)
    def get_torrent_list(self):
        url = urljoin(self.host, "torrents.php")
        return self.request_handler.get(url)

    @retry(delay=180)
    def get_torrent_detail(self, torrent_id):
        url = urljoin(self.host, f"details.php?id={torrent_id}")
        return self.request_handler.get(url)

    @retry(delay=180)
    def download_torrent(self, torrent_id, passkey):
        url = urljoin(self.host, f"download.php?id={torrent_id}&passkey={passkey}")
        return self.request_handler.get(url)

    @retry(delay=180)
    def get_usercp(self):
        url = urljoin(self.host, f"usercp.php")
        return self.request_handler.get(url)


class NexusUser(provider.PTUser):
    def __init__(self, client: NexusHttpClient, language: National):
        self.user_id = None
        self.passkey = ""
        self.client = client
        self.language = language
        self.already_attendance = True
        self.user_name = ""
        self.user_level = ""
        self.karma_points = ""
        self.sharing_rate = ""
        self.upload_size = ""
        self.download_size = ""
        self.upload_time = ""
        self.download_time = ""
        self.torrent_upload_count = ""
        self.torrent_download_count = ""
        self.connect_able = ""
        self.connect_limit = ""
        self.ip_addr = ""
        self.bt_client = ""
        self.seeding_time = ""
        self.download_time = ""
        self.hit_and_run_count = ""
        self.current_seeding_torrents = []
        self.current_leeching_torrents = []
        self._init_user_info()

    def _init_user_info(self):
        resp = self.client.get_index().content
        if not resp:
            raise ValueError("[Nexus] user information acquisition failed")
        dom = etree.HTML(resp)
        for href in dom.xpath("//a/@href"):
            if "attendance.php" in href:
                self.already_attendance = False
            if "userdetails.php" in href:
                match = re.findall(r".*id=(\d*)", href)
                self.user_id = match[0] if match else None
        if self.user_id:
            self.get_user_detail()
            self.get_passkey()
            self.current_seeding_torrents = self.get_current_seeding()
            self.current_leeching_torrents = self.get_current_leeching()

    def get_passkey(self):
        resp = self.client.get_usercp()
        dom = etree.HTML(resp.text)
        texts = dom.xpath("//td/text()")
        for text in texts:
            match = re.findall(r"[a-z\d]*", text)
            if match and len(match[0]) == 32:
                self.passkey = match[0]
                return

    def get_user_detail(self):
        resp = self.client.get_user_detail(self.user_id).content
        if not resp:
            logging.warning("[Nexus] user detail acquisition failed")
            return
        dom = etree.HTML(resp)
        user_info = dom.xpath("//h1//text()")
        self.user_name = user_info[0] if user_info else ""
        body_table = dom.xpath("//table[@class='main']//table[@width='100%']")[0]
        for tr in body_table.xpath(".//tr"):
            if len(tr) != 2:
                continue
            name = tr[0].xpath("./text()")[0].strip()
            if name == self.language.ip_addr:
                self.ip_addr = "".join(tr[1].xpath("./text()"))
            elif name == self.language.hit_and_run:
                self.hit_and_run_count = "".join(tr[1].xpath("./text()"))
            elif name == self.language.bt_client:
                self.bt_client = "".join(tr[1].xpath("./text()"))
            elif name == self.language.karma_points:
                self.karma_points = "".join(tr[1].xpath("./text()"))
            elif name == self.language.transfers:
                self.get_transfers(tr[1])
            elif name == self.language.level:
                self.user_level = self.get_user_level(tr[1])
            elif name == self.language.torrenting_time:
                self.get_torrenting_time(tr[1])

    def get_transfers(self, dom):
        uploaded_gb = 0
        downloaded_gb = 0
        for tr in dom.xpath(".//tr"):
            for td in tr.xpath(".//td"):
                text = "".join(td.xpath(".//text()"))
                if self.language.uploaded in text:
                    result = re.findall(r"([\d\.]+) ([a-zA-Z]+)", text)
                    uploaded = result[0] if result else None
                    uploaded_gb = torrent_size_translater.get(uploaded[1])(uploaded[0])
                if self.language.downloaded in text:
                    result = re.findall(r"([\d\.]+) ([a-zA-Z]+)", text)
                    downloaded = result[0] if result else None
                    downloaded_gb = torrent_size_translater.get(downloaded[1], lambda x: None)(downloaded[0])
        rate = round(uploaded_gb / downloaded_gb, 2) if all([downloaded_gb, uploaded_gb]) else None
        self.download_size = downloaded_gb
        self.upload_size = uploaded_gb
        self.sharing_rate = rate

    @staticmethod
    def get_user_level(dom):
        match = dom.xpath("./img/@title")
        return match[0] if match else ""

    def get_torrenting_time(self, dom):
        for tr in dom.xpath(".//tr"):
            for td in tr.xpath(".//td"):
                text = "".join(td.xpath(".//text()"))
                if self.language.seeding_time in text:
                    pattern = f"{self.language.seeding_time}:\s*([^\s.]*)\s*"
                    result = re.findall(pattern, text)
                    self.upload_time = result[0] if result else None
                if self.language.leeching_time in text:
                    pattern = f"{self.language.leeching_time}:\s*([^\s.]*)\s*"
                    result = re.findall(pattern, text)
                    self.download_time = result[0] if result else None

    def get_rss_basket_link(self) -> str:
        resp = self.client.rss_basket()
        if not resp:
            return ""
        dom = etree.HTML(resp.content)
        for value in dom.xpath("//input/@value"):
            if "passkey" in value:
                return value

    def get_current_seeding(self):
        resp = self.client.get_user_torrent_list(self.user_id, "seeding").text
        if not resp:
            raise ValueError("[Nexus] user current seeding acquisition failed")
        dom = etree.HTML(resp)
        count = dom.xpath("//b/text()")
        self.torrent_upload_count = count[0] if count else ""
        torrents = []
        titles = []
        for td in dom.xpath("//tr[1]/td"):
            hs_img = td.xpath(".//img/@alt")
            if hs_img:
                titles.append(hs_img[0])
            else:
                text = td.xpath("./text()")
                titles.append(text[0] if text else None)
        for tr in dom.xpath("//tr")[1:]:
            torrents.append(NexusTorrent.init_torrent_from_html(tr, titles, self.language))
        return torrents

    def get_current_leeching(self):
        resp = self.client.get_user_torrent_list(self.user_id, "leeching").text
        if not resp:
            raise ValueError("[Nexus] user current leeching acquisition failed")
        dom = etree.HTML(resp)
        count = dom.xpath("//b/text()")
        self.torrent_upload_count = count[0] if count else ""
        torrents = []
        titles = []
        for td in dom.xpath("//tr[1]/td"):
            hs_img = td.xpath(".//img/@alt")
            if hs_img:
                titles.append(hs_img[0])
            else:
                titles.append("".join([t.strip() for t in td.xpath("./text()")]))
        for tr in dom.xpath("//tr")[1:]:
            torrents.append(NexusTorrent.init_torrent_from_html(tr, titles, self.language))
        return torrents

    @property
    def data(self):
        return {
            "username": self.user_name,
            "passkey": self.passkey,
            "rss_basket": self.get_rss_basket_link(),
            "karma": self.karma_points,
            "sharing_rate": self.sharing_rate,
            "upload_size": f"{self.upload_size} GB" if self.upload_size else "",
            "download_size": f"{self.download_size} GB" if self.download_size else "",
            "seeding_time": self.upload_time,
            "download_time": self.download_time,
            "seeding_count": len(self.current_seeding_torrents),
            "download_count": len(self.current_leeching_torrents),
            "ipaddr": self.ip_addr,
            "bt_client": self.bt_client,
            "H&R": self.hit_and_run_count,
            "current_leeching_torrents": self.current_leeching_torrents,
            "current_seeding_torrents": self.current_seeding_torrents,
        }

    def __repr__(self):
        return f"NexusUser<{f'{self.user_name}:{self.user_id}' if self.user_id else 'anonymous'}>"


class NexusPHPPTProvider(provider.PTProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader):
        self.name = name
        self._init_property(config_reader)

    def _init_property(self, config_reader: AbsConfigReader):
        config = config_reader.read()
        self.enable = config.get('enable', False)
        if not self.enable:
            return
        main_url = config.get('main_link', '')
        cookie = config.get('cookie', '')
        self.nexus_client = NexusHttpClient(main_url, helper.get_request_controller(cookie))
        language = config.get('language')
        if language is None:
            logging.warning("[Nexus] language missing, use default simplified_chinese")
            language = 'simplified_chinese'
        elif language not in national_named_tuple._fields:
            logging.error(
                "[Nexus] language <%s> config error, please choose from %s, use default simplified_chinese",
                language, national_named_tuple._fields
            )
            language = 'simplified_chinese'
        self.national = National(language)
        self.rss_subscribe_link = config.get('rss_subscribe_link', '')
        self.download_provider = config.get('downloader', '')
        self.keeping_time = config.get('keeping_time', 120)
        self.max_sum_size = config.get('max_sum_size', 200.0)
        self.max_seeding = config.get('max_seeding', 20)
        self.attendance = bool(config.get('attendance', False))
        self.html_links = config.get('html_links', [])

    def get_pt_user(self) -> NexusUser:
        nexus_user = NexusUser(self.nexus_client, self.national)
        logging.info("[Nexus] get Nexus user %s", nexus_user)
        return nexus_user

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

    def get_torrents(self, user: NexusUser):
        # TODO add rss basket torrents
        xml_torrents = self.get_torrent_from_xml()
        html_torrents = self.get_torrent_from_html()
        current_leeching_torrents = user.current_leeching_torrents
        current_seeding_torrents = user.current_seeding_torrents
        torrents = NexusTorrent.merge_torrents(
            xml_torrents + html_torrents + current_leeching_torrents + current_seeding_torrents)
        effective_torrent = []
        for torrent in torrents:
            if not torrent.is_effective_torrent:
                torrent.update_property(self.nexus_client.get_torrent_detail(torrent.id))
            if torrent.is_effective_torrent:
                effective_torrent.append(torrent)
        return torrents

    def need_delete_torrents(self, **kwargs):
        return

    def filter_torrents_for_deletion(self, user: NexusUser, max_sum_size: float, download_sum_size: float):
        """
        Torrent that need to be deleted:
        - Torrent is downloading, but free has expired
        - The torrent has no upload value (the torrent has been downloaded, but the free has expired and there is no upload volume)
        Torrent that need`t to be deleted
        - The torrent is in the user's collection
        """
        need_remove_torrents = []
        # keeping torrents forever
        if self.keeping_time == -1:
            return need_remove_torrents
        # need release disk space or change torrents for seeding
        if download_sum_size >= (0.8 * max_sum_size) or len(
                user.current_seeding_torrents + user.current_leeching_torrents) >= self.max_seeding:
            # TODO Remove the torrent from the collection before filter
            # TODO query the seeding model filter the no upload seeding task for delete
            for torrent in copy.deepcopy(user.current_seeding_torrents):
                if torrent.need_remove:
                    need_remove_torrents.append(torrent)
                    user.current_seeding_torrents.remove(torrent)
            for torrent in copy.deepcopy(user.current_leeching_torrents):
                if torrent.need_remove:
                    need_remove_torrents.append(torrent)
                    user.current_leeching_torrents.remove(torrent)
        return need_remove_torrents

    def filter_torrents_for_download(self, user: NexusUser) -> list[NexusTorrent]:
        """
        需要下载的种子描述:
        - 未下载的免费种子
        - 用户收藏种子 # TODO
        """
        torrents = self.get_torrents(user)
        need_download_count = self.max_seeding - len(user.current_seeding_torrents + user.current_leeching_torrents)
        need_download_torrent = []
        for torrent in torrents:
            if torrent.is_free and not torrent.downloading and not torrent.download_complete:
                need_download_torrent.append(torrent)
        sorted(need_download_torrent, key=lambda x: x.d())
        if need_download_count > 0:
            return need_download_torrent[:need_download_count]
        return []

    def get_torrent_from_html(self) -> list:
        torrents = []
        try:
            for link in self.html_links:
                resp = self.nexus_client.get(link)
                dom = etree.HTML(resp.content)
                trs = dom.xpath('//table[@class="torrents"]/tr')
                if len(trs) > 1:
                    columns = []
                    for td in trs[0].xpath("./td"):
                        alts = td.xpath(".//img/@alt")
                        alt = alts[0] if alts else None
                        if self.national.is_img_alt_attribute(alt):
                            columns.append(alt)
                        else:
                            text = "".join([t.strip() for t in td.xpath(".//text()")])
                            columns.append(text)
                    for tr in trs[1:]:
                        torrent = NexusTorrent.init_torrent_from_html(tr, columns, self.national)
                        torrents.append(torrent)
            logging.info("[%s] html find %d torrents", self.name, len(torrents))
        except Exception as err:
            logging.error('[%s] parse html torrents error:%s', err)
        return torrents

    def get_torrent_from_xml(self) -> list[NexusTorrent]:
        rss_subscribe_torrents = self.get_torrent_from_rss_subscribe()
        rss_basket_torrents = self.get_torrent_from_rss_basket()
        return rss_subscribe_torrents + rss_basket_torrents

    def get_torrent_from_rss_basket(self) -> list[NexusTorrent]:
        # TODO  Implement rss basket
        return []

    def get_torrent_from_rss_subscribe(self) -> list[NexusTorrent]:
        torrents = []
        try:
            resp = self.nexus_client.get(self.rss_subscribe_link, timeout=30)
            if not resp:
                logging.error("[Nexus] rss subscribe page acquisition failed")
                return torrents
            xml_parse = etree.parse(io.BytesIO(resp.content))
            items = xml_parse.findall('.//item')
            for item in items:
                torrent = NexusTorrent.init_torrent_from_xml(item)
                torrent.update_property(
                    self.nexus_client.get_torrent_detail(torrent.id),
                    self.national
                )
            logging.info("[Nexus] rss subscribe find %d torrents", len(torrents))
        except Exception as err:
            logging.error('[Nexus] parse rss subscribe error:%s', err)
        return torrents

    def go_attendance(self, user: NexusUser) -> None:
        if self.attendance:
            try:
                if not user.already_attendance:
                    if getattr(self.nexus_client.attendance(), "status_code") == 200:
                        logging.info("[Nexus] Do attendance(%s) with %s success", self.name, user)
            except Exception as err:
                logging.warning("[Nexus] Do attendance(%s) with %s error:%s", self.name, user, err)

    def get_download_provider(self) -> str:
        return self.download_provider

    def get_max_sum_size(self) -> float:
        return float(self.max_sum_size)

    def get_keeping_time(self) -> int:
        return self.keeping_time

    def download_torrent_file(self, user: NexusUser, torrent: NexusTorrent) -> [io.BytesIO, None]:
        content = getattr(self.nexus_client.download_torrent(torrent.id, user.passkey), "content")
        if not content:
            logging.error('[Nexus] download torrent(%d) content failed', torrent.id)
            return None
        return io.BytesIO(content)
