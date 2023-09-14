import logging
import os
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import DownloadTasks, DownloadProviders, SourceProviders
from utils import helper, global_config
from utils.helper import retry
from api import types
from api.values import Resource, Task, Downloader, CFG_BASE_PATH
from download_provider.provider import DownloadProvider


class KubespiderDownloader:
    def __init__(self, download_providers: list[DownloadProvider]):
        self.download_providers: list[DownloadProvider] = download_providers
        self.session = self.get_db_session()

    @staticmethod
    def get_db_session() -> Session:
        db_uri = f"sqlite:///{os.path.join(CFG_BASE_PATH, 'kubespider.db')}"
        engine = create_engine(db_uri)
        session = sessionmaker(bind=engine)()
        return session

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

    def download_file(self, resource: Resource, downloader: Downloader = None) -> [Exception, Task]:
        downloader_list = self.download_providers
        if downloader is not None:
            # If downloader is specified, only use this downloader
            downloader_list = self.filter_bind_downloader(downloader)

        if downloader_list is None or len(downloader_list) == 0:
            logging.error('Downloader not found, check your configuration!!!')
            return TypeError('Downloader not found, check your configuration!!!')
        link_type = resource.link_type
        logging.info('download link type %s, with provider size %s', link_type, len(downloader_list))
        if link_type == types.LINK_TYPE_TORRENT:
            result = self.handle_torrent_download(resource, downloader_list)

        elif link_type == types.LINK_TYPE_MAGNET:
            result = self.handle_magnet_download(resource, downloader_list)

        elif link_type == types.LINK_TYPE_GENERAL:
            result = self.handle_general_download(resource, downloader_list)
        else:
            logging.warning("Unknown link type:%s", link_type)
            result = None
        if isinstance(result, Task):
            downloader = self.session.query(DownloadProviders).filter_by(name=result.download_provider_name).first()
            source = self.session.query(SourceProviders).filter_by(name=result.resource_provider_name).first()
            instance = self.session.query(DownloadTasks).filter_by(task_id=result.uid).first() or DownloadTasks()
            instance.task_id = result.uid
            instance.title = result.title
            instance.desc = result.desc
            instance.file_size = result.file_size
            instance.file_type = result.file_type
            instance.download_path = result.download_path
            instance.download_provider_id = downloader.id if downloader else None
            instance.source_provider_id = source.id if source else None
            self.session.add(instance)
            self.session.commit()
        return result

    @retry(delay=0.3)
    def handle_torrent_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> [Exception, Task]:
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
            result = provider.send_torrent_task(Task(
                url=tmp_file,
                path=resource.path,
                link_type=types.LINK_TYPE_TORRENT,
                torrent_content=resource.torrent_content
            ))
            if isinstance(result, Exception):
                logging.warning('Download torrent file error:%s', err)
                continue
            return result
        return err

    @retry(delay=0.3)
    def handle_magnet_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> [Exception, Task]:
        result = None
        for provider in downloader_list:
            logging.info('Download magent file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            result = provider.send_magnet_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LINK_TYPE_MAGNET,
                **resource.extra_params()
            ))
            if isinstance(result, Exception):
                logging.warning('Download torrent file error:%s', result)
                continue
            # use the first successful downloader
            return result
        return result

    @retry(delay=0.3)
    def handle_general_download(self, resource: Resource, downloader_list: list[DownloadProvider]) -> [Exception, Task]:
        result = None
        for provider in downloader_list:
            logging.info('Download general file with downloader(%s)', provider.get_provider_name())
            provider.load_config()
            result = provider.send_general_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LINK_TYPE_GENERAL,
                **resource.extra_params()
            ))
            if isinstance(result, Exception):
                logging.warning('Download torrent file error:%s', result)
                continue
            # use the first successful downloader
            return result
        return result

    def handle_download_remove(self, downloader: Downloader, tasks: list[Task]) -> list:
        downloader_list = None

        if downloader is not None:
            downloader_list = self.filter_bind_downloader(downloader)

        # If downloader_list is None, do nothing
        if downloader_list is None or len(downloader_list) == 0:
            return

        for provider in downloader_list:
            provider.load_config()
            removed_tasks = provider.remove_tasks(tasks)
            for task in removed_tasks:
                instance = self.session.query(DownloadTasks).filter_by(task_id=task.uid).first()
                if instance:
                    instance.is_deleted = True
                    self.session.add(instance)
            self.session.commit()
            return removed_tasks
        return []

    def __del__(self):
        if self.session:
            self.session.close()


kubespider_downloader: KubespiderDownloader = KubespiderDownloader(None)
