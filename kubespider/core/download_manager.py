# -*- coding: utf-8 -*-
import queue
import time
import logging

from flask import Flask

import download_provider
from download_provider import DownloadProvider
from utils import helper, types, global_config
from utils.config_reader import YamlFileConfigReader
from utils.helper import retry
from utils.values import Config, Extra, Resource, Task, Downloader


class DownloadManager:
    def __init__(self, app=None) -> None:
        self.download_config = YamlFileConfigReader(Config.DOWNLOAD_PROVIDER.config_path())
        self.queue = queue.Queue(maxsize=100)
        self.instances = {}
        if app:
            self.init_app(app)
        self.reload_instance()

    def init_app(self, app: Flask):
        if "download_manager" in app.extensions:
            raise RuntimeError(
                "A 'DownloadManager' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        app.extensions["download_manager"] = self

    @staticmethod
    def get_definitions():
        return [provider.definitions().serializer() for provider in download_provider.providers]

    def get_confs(self) -> dict:
        download_config = self.download_config.read()
        data = {}
        for key, conf in download_config.items():
            if key in self.instances.keys():
                conf["is_alive"] = self.instances[key].is_alive
            else:
                conf["is_alive"] = False
            data[key] = conf
        return data

    def create_or_update(self, reload=True, **kwargs):
        name = kwargs.get("name")
        config = self.download_config.read()
        exists = config.get(name)
        extra_params = {}
        if exists:
            extra_params.update(exists)
        extra_params.update(kwargs)
        config_type = extra_params.pop('type')
        enable = extra_params.pop('enable')
        notification_config = DownloadConfig(config_type, enable, **extra_params)
        notification_config.validate()

        config[name] = notification_config.to_dict()
        self.download_config.save(config)
        if reload:
            self.reload_instance()

    def remove(self, name, reload=True):
        config = self.download_config.read()
        config.pop(name, None)
        self.download_config.save(config)
        if reload:
            self.reload_instance()

    def reload_instance(self):
        for name, conf in self.get_confs().items():
            try:
                if conf.get("enable"):
                    cls = DownloadConfig.get_provider_by_type(conf.get("type"))
                    definitions = cls.definitions()
                    params = {}
                    for arg_name in definitions.arguments.keys():
                        params[arg_name] = conf.get(arg_name)
                    if not params.get("name"):
                        params["name"] = name
                    # pylint: disable=E1102
                    instance = cls(**params)
                    self.instances[name] = instance
                    logging.info('[DownloadManager] %s enabled...', name)
            except Exception as err:
                logging.warning('[DownloadManager] %s enabled failed, %s', name, err)
        logging.info("[DownloadManager] instance reload success ...")

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
        print(download_providers)
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
        print(download_providers)
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

        if link_type == types.LINK_TYPE_TORRENT:
            return self.handle_torrent_download(resource, downloader_list)

        if link_type == types.LINK_TYPE_MAGNET:
            return self.handle_magnet_download(resource, downloader_list)

        if link_type == types.LINK_TYPE_GENERAL:
            return self.handle_general_download(resource, downloader_list)

        logging.warning("[DownloadManager] Unknown link type:%s", link_type)

    def period_run(self):
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
            logging.info('Download magent file with downloader(%s)', provider.name)
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
            logging.info('Download general file with downloader(%s)', provider.name)
            err = provider.send_general_task(Task(
                url=resource.url,
                path=resource.path,
                link_type=types.LINK_TYPE_GENERAL,
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


class DownloadConfig(Extra):
    def __init__(self, config_type: str, enable: bool, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = kwargs.get("name")
        self.type = config_type
        self.enable = enable

    @classmethod
    def get_provider_by_type(cls, _type: str):
        _type: str = cls.translate_type(_type)
        provider_cls = getattr(download_provider, _type, None)
        if not provider_cls:
            raise ValueError("type missing or invalid")
        return provider_cls

    def validate(self):
        provider = self.get_provider_by_type(self.type)
        definition = provider.definitions()
        definition.validate(**self.extra_params())

    @staticmethod
    def translate_type(_type: str) -> str:
        type_split = _type.split("_")
        if len(type_split) > 1:
            return "".join([i.capitalize() for i in type_split])
        return _type

    def to_dict(self) -> dict:
        provider = self.get_provider_by_type(self.type)
        return {
            "type": provider.__name__,
            "enable": bool(self.enable),
            **self.extra_params()
        }


kubespider_download_server: DownloadManager = None
