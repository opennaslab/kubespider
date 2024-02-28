import json
from flask import request
from api.response import success
from api.v2.binding import binding_blu
from core import plugin_binding


@binding_blu.route('', methods=['GET'])
def list_binding_handler():
    data = plugin_binding.kubespider_plugin_binding.list_config()
    return success([config.to_dict() for config in data])


@binding_blu.route('', methods=['PUT'])
def create_binding_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    plugin_binding.kubespider_plugin_binding.add(data)
    return success()


@binding_blu.route('/<name>', methods=['POST'])
def update_binding_handler(name: str):
    data: dict = json.loads(request.data.decode("utf-8"))
    plugin_binding.kubespider_plugin_binding.update(name, data)
    return success()


@binding_blu.route('/<name>', methods=['DELETE'])
def remove_binding_handler(name: str):
    plugin_binding.kubespider_plugin_binding.remove(name)
    return success()
