import abc
import logging
import os
import uuid

from flask import Flask
from core.models import ProviderInstance, db
from utils.config_reader import YamlFileConfigReader
from utils.helper import get_provider_conf_base_path
from utils.values import ProviderApiSaveParams


class AbsManager:
    @abc.abstractmethod
    def __init__(self, app: Flask = None):
        self.instance = {}
        self.provider_type = ""  # ProviderType

    @abc.abstractmethod
    def init_app(self, app: Flask):
        pass

    @abc.abstractmethod
    def reload_instance(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_specs():
        pass

    def get_instance_confs(self, instance_id=None, instance_name=None) -> [None, dict, list]:
        if instance_id:
            instance = ProviderInstance.query.filter(
                ProviderInstance.id == instance_id, ProviderInstance.provider_type == self.provider_type).first()
            data = instance.to_dict() if instance else None
            if data:
                active_obj = self.instance.get(instance.id)
                data['active'] = True if active_obj else False
            return data
        elif instance_name:
            instance = ProviderInstance.query.filter(
                ProviderInstance.name == instance_name, ProviderInstance.provider_type == self.provider_type).first()
            data = instance.to_dict() if instance else None
            if data:
                active_obj = self.instance.get(instance.id)
                data['active'] = True if active_obj else False
            return data
        else:
            instances = []
            for instance in ProviderInstance.query.filter(ProviderInstance.provider_type == self.provider_type).all():
                data = instance.to_dict()
                active_addr = self.instance.get(instance.id)
                data['active'] = True if active_addr else False
                instances.append(data)
            return instances

    def save_conf(self, params: ProviderApiSaveParams, reload=True) -> [None, str]:
        if not params.is_validate:
            return f"params not validate or validate failed"
        if params.id:
            instance = ProviderInstance.query.filter(
                ProviderInstance.id == params.id, ProviderInstance.provider_type == self.provider_type).first()
            conf_file = instance.conf_file
            if not instance:
                return f"instance: {params.id} not exist"
        else:
            instance = ProviderInstance()
            conf_file = f"{uuid.uuid1()}.yaml"
        base_path = get_provider_conf_base_path(params.provider_type)
        YamlFileConfigReader(os.path.join(base_path, conf_file)).save(params.data)
        instance.name = params.instance_name
        instance.provider_name = params.provider_name
        instance.provider_type = params.provider_type
        instance.conf_file = conf_file
        db.session.add(instance)
        db.session.commit()
        if reload:
            self.reload_instance()

    def delete_conf(self, instance_id) -> [None, str]:
        instance = ProviderInstance.query.filter(
            ProviderInstance.id == instance_id, ProviderInstance.provider_type == self.provider_type).first()
        if not instance:
            return f"instance: {instance_id} not exist"
        base_path = get_provider_conf_base_path(instance.provider_type)
        os.remove(os.path.join(base_path, instance.conf_file))
        db.session.delete(instance)
        db.session.commit()
        self.reload_instance()

    def partial_update_conf(self, instance_name, reload=False, **kwargs):
        """this function just support update which kwargs in instance_params"""
        try:
            for instance_id, instance in self.instance.items():
                if instance.name == instance_name:
                    instance_conf = self.get_instance_confs(instance_id=instance_id)
                    old_conf = instance_conf["conf"]
                    update = {}
                    for item in old_conf.get("instance_params"):
                        if item.get("name") in kwargs.keys():
                            value = kwargs.pop(item.get("name"))
                            item['value'] = value
                            update[item.get("name")] = value
                    params = ProviderApiSaveParams(id=instance_id, **old_conf)
                    params.validate(self)
                    if params.is_validate:
                        self.save_conf(params, reload=reload)
                        logging.info(
                            "[%s] partial update success:  <update: %s> <drop:%s>",
                            instance_name, str(update), str(kwargs)
                        )
                    else:
                        logging.info(
                            "[%s] partial update failed: params validate failed, %s",
                            instance_name, params.error)
        except Exception as err:
            logging.error(
                "[%s] partial update failed: <kwargs: %s> <err: %s>", instance_name, str(kwargs), str(err)
            )
