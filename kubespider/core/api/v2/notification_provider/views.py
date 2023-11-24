from flask import request, current_app

from core.api.response import success, param_error
from core.api.v2.notification_provider import notification_provider_blu
from utils.values import ProviderApiSaveParams


@notification_provider_blu.route("/spec", methods=["GET"])
def get_notification_providers():
    notification_manager = current_app.extensions['notification_manager']
    specs = notification_manager.get_specs()
    return success(specs)


@notification_provider_blu.route("/instance", methods=["GET", "POST", "PUT", "DELETE"])
def notification_provider_instance():
    notification_manager = current_app.extensions['notification_manager']
    if request.method == 'GET':
        instance_confs = notification_manager.get_instance_confs()
        return success(instance_confs)
    elif request.method == 'POST':
        params = ProviderApiSaveParams(**request.json)
        if params.validate(notification_manager):
            exc = notification_manager.save_conf(params)
            if not exc:
                return success()
            else:
                return param_error(exc)
        else:
            return param_error(params.error)
    elif request.method == 'PUT':
        conf = request.json.get("conf", {})
        instance_id = request.json.get("id")
        params = ProviderApiSaveParams(id=instance_id, **conf)
        if params.validate(notification_manager):
            exc = notification_manager.save_conf(params)
            if not exc:
                return success()
            else:
                return param_error(exc)
        else:
            return param_error(params.error)
    elif request.method == 'DELETE':
        instance_id = request.json.get("id")
        conf = notification_manager.get_instance_confs(instance_id=instance_id)
        if not conf:
            return param_error("instance not exist")
        exc = notification_manager.delete_conf(instance_id)
        if not exc:
            notification_manager.reload_instance()
            return success()
        else:
            return param_error(exc)


@notification_provider_blu.route("/send_message", methods=["POST"])
def send_message():
    notification_manager = current_app.extensions['notification_manager']
    title = request.json.get("title")
    params = request.json.get("params")
    notification_manager.send_message(title=title, **params)
    return success()
