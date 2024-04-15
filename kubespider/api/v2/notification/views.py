import json
from flask import request
from api.response import success
from api.v2.notification import notification_blu
from core.notification_manager import notification_manager


@notification_blu.route('', methods=['GET'])
def list_notification_definitions():
    definitions = notification_manager.get_definitions()
    return success(data=definitions)


@notification_blu.route('/configs', methods=['GET'])
def list_notification_configs():
    configs = notification_manager.get_confs()
    return success(data=configs)


@notification_blu.route('/configs', methods=['POST'])
def modify_notification_config():
    data: dict = request.json
    notification_manager.create_or_update(**data)
    return success()


@notification_blu.route('/configs/<config_id>', methods=['DELETE'])
def delete_notification_config(config_id):
    notification_manager.remove(config_id)
    return success()


@notification_blu.route('/send_message', methods=['POST'])
def send_message():
    data: dict = json.loads(request.data.decode("utf-8"))
    title = data.pop('title', "")
    notification_manager.send_message(title=title, **data)
    return success()
