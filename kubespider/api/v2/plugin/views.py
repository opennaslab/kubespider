import json
from flask import request
from api.response import success
from api.v2.plugin import plugin_blu
from core import plugin_manager


@plugin_blu.route('', methods=['GET'])
def list_plugin_handler():
    plugins = plugin_manager.kubespider_plugin_manager.list_plugin()
    return success([plugin.to_dict() for plugin in plugins])


@plugin_blu.route('', methods=['PUT'])
def register_plugin_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    if 'definition' not in data:
        raise Exception("definition is required")
    plugin_manager.kubespider_plugin_manager.register(data['definition'])
    return success()


@plugin_blu.route('/<plugin_name>', methods=['POST'])
def operator_plugin_handler(plugin_name):
    data: dict = json.loads(request.data.decode("utf-8"))
    if 'enable' in data:
        if data['enable']:
            plugin_manager.kubespider_plugin_manager.enable(plugin_name)
        else:
            plugin_manager.kubespider_plugin_manager.disable(plugin_name)
    return success()

@plugin_blu.route("/<plugin_name>", methods=['DELETE'])
def unregister_plugin_handler(plugin_name):
    plugin_manager.kubespider_plugin_manager.unregister(plugin_name)
    return success()


@plugin_blu.route("/<plugin_name>", methods=['UPDATE'])
def update_plugin_handler(plugin_name):
    data: dict = json.loads(request.data.decode("utf-8"))
    if 'definition' not in data:
        raise Exception("definition is required")
    plugin_manager.kubespider_plugin_manager.unregister(plugin_name)
    plugin_manager.kubespider_plugin_manager.register(data['definition']) 
    return success()
