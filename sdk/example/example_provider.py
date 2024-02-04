from kubespider_source_provider_sdk import SDK, ProviderType


@SDK(ProviderType.parser)
class Provider:

    @staticmethod
    # pylint: disable=unused-argument
    def get_links(source: str, **kwargs):
        return [{
            "url": "magnet:?xt=urn:btih:a8b6f7915bf8136a655b6e17c152838aaf52ee74&dn=元宇宙回到1995第1集.mp4",
            "path": "元宇宙回到1995",
            "file_type": "video_mixed",
            "link_type": "magnet",
        }]

    @staticmethod
    # pylint: disable=unused-argument
    def should_handle(source: str, **kwargs):
        return True
