from download_provider import provider

class MotrixDownloadProvider(provider.DownloadProvider):
    def __init__(self) -> None:
        self.provider_name = 'motrix_download_provider'
        self.rpc_endpoint = ''
        pass

    def get_provider_name(self):
        return self.provider_name

    def send_task(self):
        pass

    def load_config(self, config):
        self.rpc_endpoint = config["RPC_ENDPOINT"]
