# This works for: https://www.btbtt12.com
# Function: download single video link
import logging
from urllib.parse import urlparse

from source_provider import provider
from api import types

class Btbtt12DisposableSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.file_type = 'torrent'
        self.webhook_enable = True
        self.provider_name = 'btbtt12_disposable_source_provider'

    def get_provider_name(self):
        return self.provider_name

    def get_provider_type(self):
        return self.provider_type

    def get_file_type(self):
        return self.file_type

    def get_download_path(self):
        return "common"

    def provider_enabled(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg['ENABLE'] == 'true'

    def is_webhook_enable(self):
        return self.webhook_enable

    def should_handle(self, dataSourceUrl):
        parse_url = urlparse(dataSourceUrl)
        if parse_url.hostname == 'www.btbtt12.com' and 'attach-download-fid' in parse_url.path:
            logging.info(f'{dataSourceUrl} belongs to Btbtt12DisposableSourceProvider')
            return True
        return False

    def get_links(self, dataSourceUrl):
        return [dataSourceUrl]
    
    def update_config(self, reqPara):
        pass
    
    def load_config(self):
        pass