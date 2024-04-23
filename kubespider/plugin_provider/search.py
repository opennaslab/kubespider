import copy

from utils.values import Resource, SearchEvent


class SearchProvider:

    def __init__(self, plugin_bind, plugin_instance):
        self.bind = plugin_bind
        self.plugin_instance = plugin_instance

    def get_provider_name(self) -> str:
        # name of source provider defined in config
        return self.bind.name

    def get_download_param(self) -> dict:
        # get the specific params for downloader
        return self.bind.arguments

    def get_search_param(self, event: SearchEvent) -> dict:
        params = copy.deepcopy(self.bind.arguments)
        params.pop('parser', {})
        params.pop('scheduler', {})
        search_params = params.pop('search', {})
        params.update(search_params)
        params.update(keyword=event.keyword, page=event.page, path=event.path, **event.extra_params())
        return params

    def get_download_provider_type(self):
        pass

    def get_prefer_download_provider(self):
        pass

    def search(self, event: SearchEvent) -> list:
        # Return the download resources for the parser provider
        result = self.plugin_instance.call_api("search", **self.get_search_param(event))
        # result:
        # {"code": 200, "msg": "Success", "data": {"page": 1, "page_size": 100, "next_page": True, "data": []}}
        # [{"code": 200, "msg": "Success", "data": {"page": 1, "page_size": 100, "next_page": True, "data": []}}]
        if isinstance(result.get("data"), dict):
            resource = result.get("data", {"page": 1, "page_size": 100, "next_page": False, "data": []})
            resource["data"] = [Resource(**item).data for item in resource.get("data", [])]
            # resource: {"page": 1, "page_size": 100, "next_page": True, "data": []}
            return [resource, ]
        else:
            resources = []
            for item in result.get("data", []):
                item["data"] = [Resource(**item).data for item in item.get("data", [])]
                # resource: {"page": 1, "page_size": 100, "next_page": True, "data": []}
                resources.append(item)
            return resources

    def __repr__(self):
        return f"<SearchProvider[bind:{self.bind.name} plugin:{self.plugin_instance.definition.name}]>"
