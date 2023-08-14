import math
import os
from urllib.parse import urljoin, quote

from source_provider import provider
from api import types
from api.values import Event, Resource
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller, retry


class AlistSourceProvider(provider.SourceProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = False
        self.provider_type = 'alist_source_provider'
        self.provider_name = name
        self.request_handler = get_request_controller()
        self.watch_dirs, self.host, self.enable, self.downloader_names, self.download_param = self._init_conf()

    def _init_conf(self):
        conf = self.config_reader.read()
        watch_dirs = [path.strip("/") for path in conf.get("watch_dirs") if path]
        host = conf.get("host", "")
        enable = conf.get('enable', True)
        downloader_names = conf.get('downloader', None)
        download_param = conf.get('download_param', {})
        return watch_dirs, host, enable, downloader_names, download_param

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return None

    def get_prefer_download_provider(self) -> list:
        if self.downloader_names is None:
            return None
        if isinstance(self.downloader_names, list):
            return self.downloader_names
        return [self.downloader_names]

    def get_download_param(self) -> dict:
        return self.download_param

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.enable

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, event: Event) -> bool:
        pass

    def get_links(self, event: Event) -> list[Resource]:
        files = []
        for path in self.watch_dirs:
            files += self.get_all_files(path)
        return files

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        pass

    @retry()
    def fs_list(self, page, per_page, path) -> tuple:
        data = {
            "path": path,
            "password": "",
            "page": page,
            "per_page": per_page,
            "refresh": False
        }
        url = urljoin(self.host, "/api/fs/list")
        resp = self.request_handler.post(url, json=data).json()
        code = resp.get("code")
        content = resp.get("data").get("content")
        alist_provider = resp.get("data").get("provider")
        total = resp.get("data").get("total")
        if code:
            return content, alist_provider, total
        raise ValueError(f"response error: {resp}")

    def list_dir(self, path="/", per_page=30):
        total_page = 1
        page = 1
        while page <= total_page:
            res = self.fs_list(page, per_page, path)
            if res:
                content, alist_provider, total = res
                total_page = math.ceil(total / per_page)
                for item in content:
                    item['provider'] = alist_provider
                    item['path'] = os.path.join(path, item.get("name")) if item.get("is_dir") else path
                    yield item
            page += 1

    def get_all_files(self, path) -> list[Resource]:
        files = []
        for item in self.list_dir(path):
            if item.get("is_dir") is True:
                new_path = os.path.join(path, item.get("name"))
                files += self.get_all_files(new_path)
            else:
                item["file_type"] = types.FILE_TYPE_COMMON
                uri = f'{os.path.join("/d", os.path.join(item.get("path"), item.get("name")))}'
                item["link"] = urljoin(self.host, quote(uri) + f'?modified={item.get("modified")}')
                files.append(Resource(
                    url=item.pop("link"),
                    path=item.pop("path"),
                    link_type=self.get_link_type(),
                    file_type=item.pop("file_type"),
                    **item
                ))
        return files
