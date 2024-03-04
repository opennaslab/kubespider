import json
from flask import request
from api.response import success, param_error
from api.v2.notification import notification_blu
from core import notification_manager
from core.notification_manager import NotificationConfigValidation


@notification_blu.route('', methods=['GET'])
def list_notification_definitions():
    definitions = notification_manager.kubespider_notification_server.get_definitions()
    return success(data=definitions)


@notification_blu.route('/configs', methods=['GET'])
def list_notification_configs():
    definitions = notification_manager.kubespider_notification_server.get_confs()
    return success(data=definitions)


@notification_blu.route('/configs/<config_name>', methods=['POST', 'PUT'])
def modify_notification_config(config_name):
    if not config_name:
        return param_error(msg='config_name is required')
    data: dict = json.loads(request.data.decode("utf-8"))
    validation = NotificationConfigValidation(**data)
    validation.validate()
    notification_manager.kubespider_notification_server.create_or_update(config_name, **validation.data)
    return success()


@notification_blu.route('/configs/<config_name>', methods=['DELETE'])
def delete_notification_config(config_name):
    if not config_name:
        return param_error(msg='config_name is required')
    notification_manager.kubespider_notification_server.remove(config_name)
    return success()


@notification_blu.route('/send_message', methods=['POST'])
def send_message():
    data: dict = json.loads(request.data.decode("utf-8"))
    title = data.pop('title', "")
    notification_manager.kubespider_notification_server.send_message(title=title, **data)
    return success()
