import logging
from flask import Flask

from core.middleware.manager import AbsManager
from core.middleware.source_provider import providers
from core.middleware.source_provider.sdk_source_provider.provider import SdkSourceProvider
from utils.types import ProviderType
from utils.values import SourceProviderApi


class SourceManager(AbsManager):

    def reload_instance(self):
        instance = {}
        for ins_conf in self.get_instance_confs():
            if ins_conf.get("enable"):
                conf = ins_conf["conf"]
                init_params = {item.get("name"): item.get("value") for item in conf.get("instance_params")}
                instance[ins_conf["id"]] = SdkSourceProvider(bin_path=conf.get("bin"), **init_params)
                logging.info(f"[SourceManager] {ins_conf.get('instance_name')} enabled, waiting for active ...")
        self.instance = instance
        logging.info("[SourceManager] instance reload success ...")

    @staticmethod
    def get_specs():
        specs = []
        for sp in providers:
            specs += sp.spec()
        return specs

    def __init__(self, app: Flask = None):
        self.provider_type = ProviderType.source_provider
        self.instance = {}
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "source_manager" in app.extensions:
            raise RuntimeError(
                "A 'Source Manager' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        with app.app_context():
            app.extensions["source_manager"] = self
            self.reload_instance()

    def active_provider_instance(self, **kwargs):
        uid = kwargs.get("uid")
        instance = self.instance.get(int(uid))
        if not instance:
            return False
        return instance.active(**kwargs)

    def search(self, keyword, sync=True):
        result = []
        for key,instance in self.instance.items():
            # if SourceProviderApi.search in instance.apis:
            if SourceProviderApi.schedule in instance.apis:
                try:
                    # resp = instance.search(sync,keyword=keyword)
                    resp = instance.schedule(sync)
                    result += resp.get("data",[])
                except Exception as err:
                    logging.error(f"[SourceProvider {instance.name}] search failed: %s",err)
        return result
