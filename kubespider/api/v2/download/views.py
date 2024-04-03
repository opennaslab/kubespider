import logging

from flask import request
from api.response import success, server_error
from api.v2.download import download_blu
from core import download_manager, source_manager, notification_manager
from utils.values import Event, Resource


@download_blu.route('', methods=['GET'])
def list_download_definitions():
    definitions = download_manager.kubespider_download_server.get_definitions()
    return success(data=definitions)


@download_blu.route('/configs', methods=['GET'])
def list_download_configs():
    configs = download_manager.kubespider_download_server.get_confs()
    return success(data=configs)


@download_blu.route('/configs', methods=['POST'])
def modify_download_config():
    data: dict = request.json
    download_manager.kubespider_download_server.create_or_update(**data)
    return success()


@download_blu.route('/configs/<config_name>', methods=['DELETE'])
def delete_download_config(config_name):
    download_manager.kubespider_download_server.remove(config_name)
    return success()


@download_blu.route('/from_url', methods=['POST'])
def tigger_with_parse():
    data: dict = request.json
    source = data.pop('dataSource')
    path = data.pop('path', '')
    logging.info('Get webhook trigger:%s', source)
    event = Event(source, path, **data)

    err = source_manager.source_provider_manager.download_with_source_provider(event)

    if err is None:
        notification_manager.kubespider_notification_server.send_message(
            title="[webhook] start download", source=source, path=path
        )
        return success()
    notification_manager.kubespider_notification_server.send_message(
        title="[webhook] download failed", source=source, path=path
    )
    return server_error(msg=str(err))


@download_blu.route('/from_resource', methods=['POST'])
def tigger_with_resource():
    resource = Resource(**request.json)
    err = download_manager.kubespider_download_server.download_file(resource)
    if err is None:
        notification_manager.kubespider_notification_server.send_message(
            title="[webhook] start download", source=resource.url, path=resource.path
        )
        return success()
    notification_manager.kubespider_notification_server.send_message(
        title="[webhook] download failed", source=resource.url, path=resource.path
    )
    return server_error(msg=str(err))
