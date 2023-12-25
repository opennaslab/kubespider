import os

from flask import jsonify, request, current_app

from core.api.response import success, server_error, param_error
from core.api.v2.source_provider import source_provider_blu
from utils.values import ProviderApiSaveParams
from utils.global_config import PathConfig


@source_provider_blu.route("/spec", methods=["GET"])
def get_source_provider_specs():
    source_manager = current_app.extensions['source_manager']
    specs = source_manager.get_specs()
    return success(data=specs)


@source_provider_blu.route("/upload", methods=["POST"])
def upload_source_provider():
    if "file" not in request.files:
        return param_error(msg="No file part")
    file = request.files['file']
    if file.filename == '' or not file:
        return param_error(msg="No selected file")
    file.save(os.path.join(PathConfig.SOURCE_PROVIDERS_BIN.config_path(), file.filename))
    return success(msg="File uploaded successfully")


@source_provider_blu.route("/instance/reply", methods=["POST"])
def receive_instance_reply():
    source_manager = current_app.extensions['source_manager']
    is_success = source_manager.active_provider_instance(**request.json)
    return success() if is_success else server_error(msg='Provider Active Failed')


@source_provider_blu.route("/instance", methods=["GET", "POST", "PUT", "DELETE"])
def source_provider_instance():
    source_manager = current_app.extensions['source_manager']
    if request.method == 'GET':
        instance_confs = source_manager.get_instance_confs()
        return success(instance_confs)
    elif request.method == 'POST':
        params = ProviderApiSaveParams(**request.json)
        if params.validate(source_manager):
            exc = source_manager.save_conf(params)
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
        if params.validate(source_manager):
            exc = source_manager.save_conf(params)
            if not exc:
                return success()
            else:
                return param_error(exc)
        else:
            return param_error(params.error)
    elif request.method == 'DELETE':
        instance_id = request.json.get("id")
        conf = source_manager.get_instance_confs(instance_id=instance_id)
        if not conf:
            return param_error("instance not exist")
        exc = source_manager.delete_conf(instance_id)
        if not exc:
            source_manager.reload_instance()
            return success()
        else:
            return param_error(exc)
