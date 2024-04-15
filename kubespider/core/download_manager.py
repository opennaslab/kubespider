# -*- coding: utf-8 -*-
import queue
import time
import logging
import traceback
import download_provider
from download_provider import DownloadProvider
from models import Download, get_session
from utils import helper, types, global_config
from utils.helper import retry
from utils.values import Resource, Task, Downloader


class DownloadManager:
    def __init__(self) -> None:
        self.queue = queue.Queue(maxsize=100)
        self.instances = {}
        self.session = get_session()

    @staticmethod
    def get_definitions():
        return [provider.definitions().serializer() for provider in download_provider.providers]

    def get_download_models(self, enable=None):
        if enable is not None:
            return self.session.query(Download).filter_by(enable=enable).all()
        return self.session.query(Download).all()

    def get_confs(self) -> dict:
        data = {}
        for instance in self.get_download_models():
            _id = instance.id
            config = instance.config
            name = instance.name
            _type = instance.type
            enable = instance.enable
            is_alive = self.instances[name].is_alive if name in self.instances.keys() else False
            config.update(name=name, type=_type, enable=enable, is_alive=is_alive, id=_id)
            data[name] = config
        return data

    def create_or_update(self, reload=True, **kwargs):
        _id = kwargs.get("id")
        name = kwargs.get("name")
        config_type = kwargs.pop('type')
        enable = kwargs.pop('enable')
        download_conf = self.session.query(Download).filter_by(id=_id).first() or Download()
        self.validate_config(config_type, **kwargs)
        download_conf.name = name
        download_conf.type = config_type
        download_conf.config = kwargs
        download_conf.enable = enable
        self.session.add(download_conf)
        self.session.commit()
        if reload:
            self.reload_instance()

    def remove(self, _id, reload=True):
        config_model = self.session.query(Download).filter_by(id=_id).first()
        if config_model:
            self.session.delete(config_model)
            self.session.commit()
            self.reload_instance()
            if reload:
                self.reload_instance()

    def reload_instance(self):
        for download_model in self.get_download_models(enable=True):
            try:
                config = download_model.config
                cls = self.get_download_provider_by_type(download_model.type)
                definitions = cls.definitions()
                params = {}
                for arg_name in definitions.arguments.keys():
                    params[arg_name] = config.get(arg_name)
                if not params.get("name"):
                    params["name"] = download_model.name
                # pylint: disable=E1102
                instance = cls(**params)
                self.instances[download_model.name] = instance
                logging.info('[DownloadManager] %s enabled...', download_model.name)
            except Exception as err:
                traceback.print_exc()
                logging.warning('[DownloadManager] %s enabled failed, %s', download_model.name, err)
        logging.info("[DownloadManager] instance reload finish ...")

    def filter_downloader_by_name(self, names: list[str], download_providers: list = None) -> list[DownloadProvider]:
        download_providers = download_providers or self.instances.values()
        return list(filter(lambda p: p.name in names, download_providers))

    def filter_downloader_by_type(self, provider_type: str, download_providers: list = None) -> list[DownloadProvider]:
        download_providers = download_providers or self.instances.values()
        return list(filter(lambda p: p.get_provider_type() == provider_type, download_providers))

    def filter_downloader_by_link_type(self, link_type: str) -> list[DownloadProvider]:
        download_providers = []
        for provider in sorted(self.instances.values(), key=lambda x: x.priority):
            if link_type in provider.supported_link_types:
                download_providers.append(provider)
        return download_providers

    def filter_bind_downloader(self, bind_downloader: Downloader) -> list[DownloadProvider]:
        download_providers = self.instances.values()
        if bind_downloader is None:
            return list(download_providers)
        download_provider_type = bind_downloader.download_provider_type
        download_provider_names = bind_downloader.download_provider_names
        logging.info('[DownloadManager] filter downloader type:%s, names:%s', download_provider_type,
                     download_provider_names)
        if download_provider_type is not None:
            # Filter by provider type
            download_providers = self.filter_downloader_by_type(download_provider_type)
        if download_provider_names is not None:
            # Filter by provider name
            download_providers = self.filter_downloader_by_name(download_provider_names, download_providers)
        return download_providers

    def download_file(self, resource: Resource, downloader: Downloader = None) -> TypeError:
        # If downloader is specified, only use this downloader
        if downloader is not None:
            downloader_list = self.filter_bind_downloader(downloader)
        # If not specified, guess downloader
        else:
            downloader_list = self.filter_downloader_by_link_type(resource.link_type)
        if not downloader_list:
            logging.error('[DownloadManager] %s download failed without a matching downloader', resource.path)
            return TypeError('Download failed without a matching downloader')
        link_type = resource.link_type
        logging.info('download link type %s, with provider size %s', link_type, len(downloader_list))

        if link_type == types.LinkType.torrent:
            return self.handle_torrent_download(resource, downloader_list)

        if link_type == types.LinkType.magnet:
            return self.handle_magnet_download(resource, downloader_list)

        if link_type == types.LinkType.general:
            return self.handle_general_download(resource, downloader_list)

        logging.warning("[DownloadManager] Unknown link type:%s", link_type)

    def period_run(self):
        logging.info('Download trigger job start running...')
        while True:
            time.sleep(180)
            for downloader in self.instances.values():
                if not downloader.is_alive:
                    logging.warning('[DownloadManager] downloader: %s is not alive', downloader.name)
            if global_config.auto_change_download_provider():
                self.handle_defective_download()

    def handle_defective_download(self):
        provider_len = len(self.instances.values())
        providers = list(self.instances.values())
        if provider_len <= 1:
            return

        # Start from the last one, the task in latest downloader will never be removed
        for index in range(provider_len - 2, -1, -1):
            # load config
            provider_now = providers[index]
            provider_next = providers[index + 1]

            tasks = provider_now.get_defective_task()
            logging.info("Find defective tasks:%d/%s", len(tasks), provider_now.name)
            for task in tasks:
                self.download_file(Resource(
                    url=task.url,
                    path=task.path,
                    link_type=task.link_type,
                ), Downloader(
                    provider_next.get_provider_type(),
                    [provider_next.name],
                ))

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
            logging.info('Download torrent file with downloader(%s)', provider.name)
            err = provider.send_torrent_task(Task(
                url=tmp_file,
                path=resource.path,
                link_type=types.LinkType.torrent,
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
            logging.info('Download magent file with downloader(%s)', provider.name)
            err = provider.send_magnet_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LinkType.magnet,
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
            logging.info('Download general file with downloader(%s)', provider.name)
            err = provider.send_general_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LinkType.general,
                **resource.extra_params()
            ))
            if err is not None:
                logging.warning('Download general file error:%s', err)
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
            provider.remove_tasks([])

    @staticmethod
    def get_download_provider_by_type(_type: str):
        provider_cls = getattr(download_provider, _type, None)
        if not provider_cls:
            raise ValueError("type missing or invalid")
        return provider_cls

    def validate_config(self, _type, **arguments):
        provider = self.get_download_provider_by_type(_type)
        definition = provider.definitions()
        definition.validate(**arguments)


download_manager: DownloadManager = DownloadManager()
