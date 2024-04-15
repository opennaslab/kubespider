import logging
from core import config_handler
from core.plugin.manager import plugin_manager
from core.plugin.binding import plugin_binding
from models.models import Binding
from plugin_provider.scheduler import SchedulerProvider
from source_provider.provider import SourceProvider
from utils.types import ProviderTypes


class SchedulerPlugin:

    @staticmethod
    def find_source_providers() -> list[SourceProvider]:
        enabled_source_providers = []
        for provider in config_handler.init_source_config():
            provider_name = provider.get_provider_name()
            try:
                if provider.provider_enabled():
                    enabled_source_providers.append(provider)
            except KeyError:
                logging.warning('[SchedulerPlugin] %s not exists, treat as disabled', provider_name)
        return enabled_source_providers

    def find_scheduler_providers(self) -> list[SchedulerProvider]:
        match_provider = []
        for provider in self.find_source_providers():
            if provider.get_provider_listen_type() == ProviderTypes.scheduler:
                match_provider.append(provider)
        # find plugin provider
        plugin_providers = self.wrap_scheduler_provider()
        return match_provider + plugin_providers

    @staticmethod
    def wrap_scheduler_provider(bindings: list[Binding] = None) -> list[SchedulerProvider]:
        binding = bindings or plugin_binding.list_config()
        providers = []
        for bind in binding:
            # wrap plugin to provider
            provider = plugin_manager.provider_maker(bind, ProviderTypes.scheduler)
            if provider:
                providers.append(provider)
        return providers

    def scheduler(self, providers: list[SchedulerProvider]):
        resource = []
        providers = providers or self.find_scheduler_providers()
        if not providers:
            logging.warning("[SchedulerPlugin] No available search providers for scheduler")
        else:
            logging.info("[SchedulerPlugin] scheduler with providers: %s", ",".join([str(p) for p in providers]))
            for provider in providers:
                result = provider.scheduler()
                result["plugin"] = provider.plugin_instance.definition.name
                resource.append(result)
        return resource


scheduler_plugin: SchedulerPlugin = SchedulerPlugin()
