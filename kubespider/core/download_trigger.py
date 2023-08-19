import logging
import time

from utils import helper, global_config
from utils.helper import retry
from api import types
from api.values import Resource, Task, Downloader
from download_provider.provider import DownloadProvider


class KubespiderDownloader:
    def __init__(self, download_providers: list[DownloadProvider]):
        self.download_providers: list[DownloadProvider] = download_providers

    def period_run(self):
        while True:
            # For certain download providers, the task start time is not available.
            # Therefore, specifying a time here would be futile.
            time.sleep(180)
            if global_config.auto_change_download_provider():
                self.handle_defective_download()

    def handle_defective_download(self):
        provider_len = len(self.download_providers)
        if provider_len <= 1:
            return

        # Start from the last one, the task in latest downloader will never be removed
        for index in range(provider_len - 2, -1, -1):
            # load config
            provider_now = self.download_providers[index]
            provider_next = self.download_providers[index + 1]

            err = provider_now.load_config()
            if err is not None:
                continue

            err = provider_next.load_config()
            if err is not None:
                continue

            tasks = provider_now.get_defective_task()
            logging.info("Find defective tasks:%d/%s", len(tasks), provider_now.get_provider_name())
            for task in tasks:
                self.download_file(Resource(
                    url=task.url,
                    path=task.path,
                    link_type=task.link_type,
                ), Downloader(
                    provider_next.get_provider_type(),
                    [provider_next.get_provider_name()],
                ))

    def filter_downloader_by_name(self, names: list[str], download_providers: list = None) -> list[DownloadProvider]:
        download_providers = download_providers or self.download_providers
        return list(filter(lambda p: p.get_provider_name() in names, download_providers))

    def filter_downloader_by_type(self, provider_type: str, download_providers: list = None) -> list[DownloadProvider]:
        download_providers = download_providers or self.download_providers
        return list(filter(lambda p: p.get_provider_type() == provider_type, download_providers))

    def filter_bind_downloader(self, bind_downloader: Downloader) -> list[DownloadProvider]:
        download_providers = self.download_providers
        if bind_downloader is None:
            return download_providers
        download_provider_type = bind_downloader.download_provider_type
        download_provider_names = bind_downloader.download_provider_names
        logging.info('filter downloader type:%s, names:%s', download_provider_type, download_provider_names)
        if download_provider_type is not None:
            # Filter by provider type
            download_providers = self.filter_downloader_by_type(download_provider_type)
        if download_provider_names is not None:
            # Filter by provider name
            download_providers = self.filter_downloader_by_name(download_provider_names, download_providers)
        return download_providers

    def download_file(self, resource: Resource, downloader: Downloader = None) -> TypeError:

        if downloader is not None:
            # If downloader is specified, only use this downloader
            downloader_list = self.filter_bind_downloader(downloader)
        else:
            downloader_list = self.download_providers

        link_type = resource.link_type

        logging.info('download link type %s, with provider size %s', link_type, len(downloader_list))
        if len(downloader_list) == 0:
            logging.error('Downloader not found, check your configuration!!!')
            return TypeError('Downloader not found, check your configuration!!!')

        if link_type == types.LINK_TYPE_TORRENT:
            return self.handle_torrent_download(resource, downloader_list)

        if link_type == types.LINK_TYPE_MAGNET:
            return self.handle_magnet_download(resource, downloader_list)

        if link_type == types.LINK_TYPE_GENERAL:
            return self.handle_general_download(resource, downloader_list)

        logging.warning("Unknown link type:%s", link_type)

        return None

    @retry(delay=0.3)
    def handle_torrent_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> TypeError:
        if resource.url.startswith('http'):
            # download torrent file
            req = helper.get_request_controller(resource.extra_param('cookies'))
            tmp_file = helper.download_torrent_file(resource.url, req)
        else:
            tmp_file = resource.url

        if tmp_file is None:
            return TypeError('Download torrent file failed')

        err = None
        for provider in downloader_list:
            logging.info('Download torrent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_torrent_task(Task(
                url=tmp_file,
                path=resource.path,
                link_type=types.LINK_TYPE_TORRENT,
                **resource.extra_params()
            ))
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            # use the first successful downloader
            break
        return err

    @retry(delay=0.3)
    def handle_magnet_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> TypeError:
        err = None
        for provider in downloader_list:
            logging.info('Download magent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_magnet_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LINK_TYPE_MAGNET,
                **resource.extra_params()
            ))
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            # use the first successful downloader
            break
        return err

    @retry(delay=0.3)
    def handle_general_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> TypeError:
        err = None
        for provider in downloader_list:
            logging.info('Download general file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            err = provider.send_general_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LINK_TYPE_GENERAL,
                **resource.extra_params()
            ))
            if err is not None:
                logging.warning('Download torrent file error:%s', err)
                continue
            # use the first successful downloader
            break
        return err

    def handle_download_remove(self, downloader: Downloader):
        downloader_list = None

        if downloader is not None:
            downloader_list = self.filter_bind_downloader(downloader)

        # If downloader_list is None, do nothing
        if downloader_list is None or len(downloader_list) == 0:
            return

        for provider in downloader_list:
            provider.load_config()
            provider.remove_tasks([])


kubespider_downloader: KubespiderDownloader = KubespiderDownloader(None)
