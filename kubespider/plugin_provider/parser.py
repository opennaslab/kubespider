from utils.values import Resource, Event


class ParserProvider:

    def __init__(self, plugin_bind, plugin_instance):
        self.bind = plugin_bind
        self.plugin_instance = plugin_instance

    def get_provider_name(self) -> str:
        # name of source provider defined in config
        return self.bind.name

    def get_download_param(self) -> dict:
        # get the specific params for downloader
        return self.bind.extra_param('download_param')

    def get_parse_param(self) -> dict:
        return self.bind.arguments

    def get_download_provider_type(self):
        pass

    def get_prefer_download_provider(self):
        pass

    def should_handle(self, event: Event) -> bool:
        response = self.plugin_instance.call_api(
            "should_handle", source=event.source, **event.extra_params(), **self.bind.arguments
        )
        return response.get('data') is True

    def get_links(self, event: Event) -> list:
        # Return the download resources for the parser provider
        # result: {"code": 200, "msg": "Success", "data": []}
        result = self.plugin_instance.call_api("get_links", source=event.source, path=event.path,
                                               **event.extra_params(), **self.bind.arguments)
        return [Resource(**item).data for item in result.get("data", [])]
