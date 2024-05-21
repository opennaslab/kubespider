# -*- coding: utf-8 -*-
import logging

from models.models import Binding
from plugin_provider.search import SearchProvider
from utils.types import ProviderTypes
from utils.values import SearchEvent
from core.plugin.manager import plugin_manager, plugin_binding


class SearchPlugin:
    def find_search_providers(self, event: SearchEvent) -> list[SearchProvider]:
        # find plugin provider, can filter provider here
        designated_providers = event.extra_params().get("search_providers", [])
        if designated_providers:
            providers = []
            for provider in self.wrap_search_provider():
                if provider.bind in designated_providers:
                    providers.append(provider)
        else:
            return self.wrap_search_provider()

    @staticmethod
    def wrap_search_provider(bindings: list[Binding] = None) -> list[SearchProvider]:
        binding = bindings or plugin_binding.list_config()
        providers = []
        for bind in binding:
            # wrap plugin to provider
            provider = plugin_manager.provider_maker(bind, ProviderTypes.search)
            if provider:
                providers.append(provider)
        return providers

    def search(self, event: SearchEvent, providers: list[SearchProvider] = None) -> list:
        resource = []
        providers = providers or self.find_search_providers(event)
        if not providers:
            logging.warning(
                "[SearchPlugin] No available search providers for search keyword: %s",
                event.keyword)
        else:
            logging.info("[SearchPlugin] search keyword: %s with providers: %s",
                         event.keyword, ",".join([str(p) for p in providers]))
            for provider in providers:
                result = provider.search(event)
                result["plugin"] = provider.plugin_instance.definition.name
                resource.append(result)
        return resource


search_plugin: SearchPlugin = SearchPlugin()
