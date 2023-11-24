from flask import current_app, request

from core.api.response import success, param_error
from core.api.v2.download_provider import download_provider_blu
from utils.values import ProviderApiSaveParams


@download_provider_blu.route("/spec", methods=["GET"])
def download_provider_middlewares():
    download_manager = current_app.extensions['download_manager']
    specs = download_manager.get_specs()
    return success(data=specs)


@download_provider_blu.route("/instance", methods=["GET", "POST", "PUT", "DELETE"])
def download_provider_instance():
    download_manager = current_app.extensions['download_manager']
    if request.method == 'GET':
        instance_confs = download_manager.get_instance_confs()
        return success(instance_confs)
    elif request.method == 'POST':
        params = ProviderApiSaveParams(**request.json)
        if params.validate(download_manager):
            exc = download_manager.save_conf(params)
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
        if params.validate(download_manager):
            exc = download_manager.save_conf(params)
            if not exc:
                return success()
            else:
                return param_error(exc)
        else:
            return param_error(params.error)
    elif request.method == 'DELETE':
        instance_id = request.json.get("id")
        conf = download_manager.get_instance_confs(instance_id=instance_id)
        if not conf:
            return param_error("instance not exist")
        exc = download_manager.delete_conf(instance_id)
        if not exc:
            download_manager.reload_instance()
            return success()
        else:
            return param_error(exc)
