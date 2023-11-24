import json
import math
import os
from urllib.parse import urljoin, quote
from kubespider_source_provider import Manager
from kubespider_source_provider.tools import retry
from kubespider_source_provider.data_types import FileType, LinkType, ProviderInstanceType, HttpApi
from kubespider_source_provider.values import Resource

manager = Manager(provider_instance_type=ProviderInstanceType.single)


@manager
class AlistSourceProvider:
    def __init__(self, name: str, host: str, watch_dirs: list, **kwargs) -> None:
        self.name = name
        self.host = host
        self.watch_dirs = [path.strip("/") for path in watch_dirs if path]
        self.cache_path = kwargs.get("cache_path", "")
        self.request_handler = kwargs.get("request_handler")()
        self.cache = self.load_cache()  # type:list

    def load_cache(self):
        cache = os.path.join(self.cache_path, self.name)
        if not os.path.exists(cache):
            return {}
        else:
            with open(cache) as f:
                return json.loads(f.read())

    def save_cache(self):
        with open(os.path.join(self.cache_path, self.name), 'w') as f:
            f.write(json.dumps(self.cache))

    @manager.registry(HttpApi.schedule)
    def schedule(self) -> list[Resource]:
        files = []
        for path in self.watch_dirs:
            files += self.get_all_files(path)
        return files

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
        if code != 200:
            raise ValueError(f"response error: {resp}")
        content = resp.get("data").get("content")
        alist_provider = resp.get("data").get("provider")
        total = resp.get("data").get("total")
        return content, alist_provider, total

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
                item["file_type"] = FileType.common
                uri = f'{os.path.join("/d", os.path.join(item.get("path"), item.get("name")))}'
                item["link"] = urljoin(self.host, quote(uri) + f'?modified={item.get("modified")}')
                files.append(Resource(
                    url=item.pop("link"),
                    path=item.pop("path"),
                    link_type=LinkType.general,
                    file_type=item.pop("file_type"),
                    **item
                ))
        return files


if __name__ == '__main__':
    manager.run()
