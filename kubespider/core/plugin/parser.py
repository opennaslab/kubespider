import logging
import os
from source_provider.provider import SourceProvider
from plugin_provider.parser import ParserProvider
from utils.values import Resource, Event, Downloader
from utils.types import ProviderTypes, FileType
from utils import helper
from core import config_handler
from core.download_manager import download_manager
from core.plugin.manager import plugin_manager, plugin_binding


class ParserPlugin:

    @staticmethod
    def find_source_providers() -> list[SourceProvider]:
        enabled_source_providers = []
        for provider in config_handler.init_source_config():
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    enabled_source_providers.append(provider)
            except KeyError:
                logging.warning('[SourceProvider] %s not exists, treat as disabled', provider_name)
        return enabled_source_providers

    def find_parse_providers(self, event: Event) -> list[SourceProvider]:
        match_provider = []
        for provider in self.find_source_providers():
            if not provider.should_handle(event) or provider.get_provider_listen_type() == ProviderTypes.parser:
                continue
            match_provider.append(provider)
        # find plugin provider
        plugin_providers = self.wrap_parser_provider()
        for provider in plugin_providers:
            if not provider.should_handle(event):
                continue
            match_provider.append(provider)
        return match_provider

    @staticmethod
    def wrap_parser_provider() -> list[ParserProvider]:
        binding = plugin_binding.list_config()
        providers = []
        for bind in binding:
            # wrap plugin to provider
            provider = plugin_manager.provider_maker(bind, ProviderTypes.parser)
            if provider:
                providers.append(provider)
        return providers

    def download_with_parser_provider(self, event: Event) -> TypeError:
        providers = self.find_parse_providers(event)
        # no provider found
        if providers is None or len(providers) == 0:
            controller = helper.get_request_controller(event.extra_param('cookies'))
            link_type = helper.get_link_type(event.source, controller)
            path = os.path.join(helper.convert_file_type_to_path(FileType.common), event.path)
            err = download_manager.download_file(Resource(
                url=event.source,
                path=path,
                file_type=FileType.common,
                link_type=link_type,
                **event.extra_params()
            ))
            return err

        errors = {}
        for provider in providers:
            links = provider.get_links(event)
            if links is None or len(links) < 1:
                continue
            for link in links:
                link.path = os.path.join(helper.convert_file_type_to_path(link.file_type), link.path)
                link.put_extra_params(provider.get_download_param())
                err = download_manager.download_file(link, Downloader(
                    provider.get_download_provider_type(),
                    provider.get_prefer_download_provider(),
                ))
                if err is not None:
                    errors[provider.get_provider_name()] = err
        if errors is not None:
            error_strings = ', '.join(
                f'download from Provider<{key}> failed with error {value}' for key, value in errors.items())
            return TypeError(error_strings)

    def parse(self, event: Event) -> list:
        resource = []
        providers = self.find_parse_providers(event)
        if not providers:
            logging.warning(
                "[ParserProviderManager] No available parse providers for parse data source: %s", event.source)
        else:
            logging.info("[ParserProviderManager] parse data source: %s with providers: %s",
                         event.source, ",".join([str(p) for p in providers]))
            for provider in providers:
                result = provider.get_links(event)
                resource += result
        return resource


parser_plugin: ParserPlugin = ParserPlugin()
