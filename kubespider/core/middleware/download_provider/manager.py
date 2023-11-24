import logging
from flask import Flask

from core.middleware.download_provider import providers
from core.middleware.manager import AbsManager
from utils.types import ProviderType
from utils.values import Resource


class DownloadManager(AbsManager):
    def __init__(self, app=None):
        self.provider_type = ProviderType.download_provider
        self.instance = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "download_manager" in app.extensions:
            raise RuntimeError(
                "A 'Download Manager' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        app.extensions['download_manager'] = self
        with app.app_context():
            self.reload_instance()

    def reload_instance(self):
        instance = {}
        providers_map = {pd.__name__: pd for pd in providers}
        for ins_conf in self.get_instance_confs():
            if ins_conf.get("enable"):
                conf = ins_conf["conf"]
                provider_cls = providers_map.get(conf["provider_name"])
                init_params = {item.get("name"): item.get("value") for item in conf.get("instance_params")}
                instance[ins_conf["id"]] = provider_cls(**init_params)
                logging.info(f"[DownloadManager] {ins_conf.get('instance_name')} enabled ...")
        self.instance = instance
        logging.info("[DownloadManager] instance reload success ...")

    def get_provider(self, resource: Resource):
        if resource.download_provider_id:
            return self.instance.get(resource.download_provider_id)
        else:
            return self.guess_download_provider(resource)

    def guess_download_provider(self, resource: Resource):
        return

    @staticmethod
    def get_specs():
        return [dp.spec() for dp in providers]
