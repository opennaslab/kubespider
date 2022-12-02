from source_provider import provider
from api import types

class TorrentSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.file_type = 'torrent'
        self.webhook_enable = True
        self.provider_name = 'torrent_source_provider'

    def should_handle(self, dataSourceUrl):
        return dataSourceUrl.endswith('.torrent')
    
    def get_provider_type(self):
        return self.provider_type
    
    def get_provider_name(self):
        return self.provider_name
    
    def load_config(self, cfg):
        pass