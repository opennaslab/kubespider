import os

from api import types
from api.values import Resource, Event, Downloader
from utils import helper
from source_provider.provider import SourceProvider
from core import period_server
from core import download_trigger


class SourceProviderManager:

    def __init__(self, source_providers: list[SourceProvider]):
        self.source_providers: list[SourceProvider] = source_providers

    def find_source_provider(self, event: Event) -> list[SourceProvider]:
        match_provider = []
        for provider in self.source_providers:
            if not provider.should_handle(event):
                continue
            match_provider.append(provider)
        return match_provider

    def download_with_source_provider(self, event: Event) -> TypeError:
        providers = self.find_source_provider(event)
        match_provider = providers[0] if len(providers) > 0 else None
        err = None
        if match_provider is None:
            controller = helper.get_request_controller(event.extra_param('cookies'))
            link_type = helper.get_link_type(event.source, controller)
            err = download_trigger.kubespider_downloader.download_file(Resource(
                url=event.source,
                path=event.path,
                file_type=types.FILE_TYPE_COMMON,
                link_type=link_type,
                **event.extra_params()
            ))
        else:
            if match_provider.get_provider_listen_type() == types.SOURCE_PROVIDER_PERIOD_TYPE:
                match_provider.update_config(event)
                err = period_server.kubespider_period_server.run_single_provider(match_provider)
            else:
                links = match_provider.get_links(event)
                if links is None or len(links) == 0:
                    return TypeError(f'No links found for {event.source}')
                for link in links:
                    link.path = os.path.join(helper.convert_file_type_to_path(link.file_type), link.path)
                    event.put_extra_params(match_provider.get_download_param())
                    err = download_trigger.kubespider_downloader.download_file(link, Downloader(
                        match_provider.get_download_provider_type(),
                        match_provider.get_prefer_download_provider(),
                    ))
                    if err is not None:
                        break
        return err


source_provider_manager: SourceProviderManager = SourceProviderManager(None)
