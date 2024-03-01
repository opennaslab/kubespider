import os

from utils.values import Resource, Event, Downloader
from utils import helper, types
from source_provider.provider import SourceProvider
from core import period_server
from core import download_trigger
from core import plugin_manager
from core import plugin_binding


class SourceProviderManager:

    def __init__(self, source_providers: list[SourceProvider]):
        self.source_providers: list[SourceProvider] = source_providers

    def find_source_provider(self, event: Event) -> list[SourceProvider]:
        match_provider = []
        for provider in self.source_providers:
            if not provider.should_handle(event):
                continue
            match_provider.append(provider)
        # find plugin provider
        plugin_providers = self.wrap_plugin_provider()
        for provider in plugin_providers:
            if not provider.should_handle(event):
                continue
            match_provider.append(provider)
        return match_provider

    def wrap_plugin_provider(self) -> list[SourceProvider]:
        binding = plugin_binding.kubespider_plugin_binding.list_config(
            types.SOURCE_PROVIDER_DISPOSABLE_TYPE)
        providers = []
        for bind in binding:
            def provider_maker(bind=bind):
                plugin_name = bind.plugin_name
                downloader = bind.extra_param('downloader')
                return type(f"{plugin_name}Provider", (SourceProvider,), {
                    "__init__": lambda self: None,
                    "get_provider_name": lambda self: bind.name,
                    "get_provider_type": lambda self: plugin_name,
                    "get_provider_listen_type": lambda self: bind.type,
                    "get_download_provider_type": lambda self: None,
                    "get_prefer_download_provider": lambda self: isinstance(downloader, list) and downloader or [downloader],
                    "get_download_param": lambda self: bind.extra_param('download_param'),
                    "get_link_type": lambda self: bind.extra_param('link_type'),
                    "provider_enabled": lambda self: True,
                    "is_webhook_enable": lambda self: True,
                    "should_handle": lambda self, event: plugin_manager.kubespider_plugin_manager.call(plugin_name, "should_handle", **{
                        'source': event.source,
                        **event.extra_params(),
                        **bind.extra_params()
                    }),
                    "get_links": lambda self, event: [Resource(**item) for item in plugin_manager.kubespider_plugin_manager.call(plugin_name, "get_links", **{
                        'source': event.source,
                        'path': event.path,
                        **event.extra_params(),
                        **bind.extra_params()
                    })],
                    "update_config": lambda self, event: None,
                    "load_config": lambda self: None,
                })
            provider = provider_maker(bind=bind)
            # wrap plugin to provider
            providers.append(provider())
        return providers

    def download_with_source_provider(self, event: Event) -> TypeError:
        providers = self.find_source_provider(event)

        # no provider found
        if providers is None or len(providers) == 0:
            controller = helper.get_request_controller(event.extra_param('cookies'))
            link_type = helper.get_link_type(event.source, controller)
            path = os.path.join(helper.convert_file_type_to_path(types.FILE_TYPE_COMMON), event.path)
            err = download_trigger.kubespider_downloader.download_file(Resource(
                url=event.source,
                path=path,
                file_type=types.FILE_TYPE_COMMON,
                link_type=link_type,
                **event.extra_params()
            ))
            return TypeError(f'No provider found and download failed with error {err}')

        result = {}
        period_providers = list(filter(lambda x: x.get_provider_listen_type() == types.SOURCE_PROVIDER_PERIOD_TYPE, providers))
        for provider in period_providers:
            provider.update_config(event)
            err = period_server.kubespider_period_server.run_single_provider(provider)
            if err is not None:
                result[provider.get_provider_name()] = err

        disposable_providers = list(filter(lambda x: x.get_provider_listen_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE, providers))
        for provider in disposable_providers:
            links = provider.get_links(event)
            if links is None or len(links) < 1:
                continue
            for link in links:
                print(link)
                link.path = os.path.join(
                    helper.convert_file_type_to_path(link.file_type), link.path)
                link.put_extra_params(provider.get_download_param())
                err = download_trigger.kubespider_downloader.download_file(link, Downloader(
                    provider.get_download_provider_type(),
                    provider.get_prefer_download_provider(),
                ))
                if err is not None:
                    result[provider.get_provider_name()] = err
        if not result:
            return None

        error_strings = ', '.join(
            f'download from Provider<{key}> failed with error {value}' for key, value in result.items())
        return TypeError(error_strings)


source_provider_manager: SourceProviderManager = SourceProviderManager(None)
