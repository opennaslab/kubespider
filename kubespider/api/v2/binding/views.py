import json
from flask import request
from api.response import success
from api.v2.binding import binding_blu
from core.plugin.binding import plugin_binding


@binding_blu.route('', methods=['GET'])
def list_binding_handler():
    data = plugin_binding.list_config()
    return success([config.serializer() for config in data])


@binding_blu.route('', methods=['POST'])
def modify_binding_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    plugin_binding.create_or_update(**data)
    return success()


@binding_blu.route('/<binding_id>', methods=['DELETE'])
def remove_binding_handler(binding_id: int):
    plugin_binding.remove(binding_id)
    return success()
