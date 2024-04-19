import json
from flask import request
from api.response import success, param_error
from api.v2.plugin import plugin_blu
from utils import helper
from utils.definition import Definition
from core.plugin.manager import plugin_manager


@plugin_blu.route('', methods=['GET'])
def list_plugin_handler():
    plugins = plugin_manager.list_plugin()
    instances = plugin_manager.list_instance()
    instance_plugin = [instance.definition.name for instance in instances]
    return success([dict(plugin.serializer(), **{"up": plugin.name in instance_plugin}) for plugin in plugins])


@plugin_blu.route('', methods=['PUT'])
def operator_plugin_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    plugin_name = data.get("name")
    enable = data.get("enable", False)
    if enable:
        plugin_manager.enable(plugin_name)
    else:
        plugin_manager.disable(plugin_name)
    return success()


def get_definition(yaml_file: [str, bytes]):
    # Download the plugin definition
    if isinstance(yaml_file, str):
        response = helper.get_request_controller().get(yaml_file, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download plugin definition: {yaml_file}")
        yaml_content = response.content
    else:
        yaml_content = yaml_file
    # Read the plugin definition
    definition = Definition.init_from_yaml_bytes(yaml_content)
    return definition


@plugin_blu.route('/register/remote', methods=['POST'])
def register_from_remote():
    data: dict = json.loads(request.data.decode("utf-8"))
    if 'definition' not in data:
        raise Exception("definition is required")
    definition = get_definition(data['definition'])
    plugin_manager.register(definition)
    return success()


@plugin_blu.route('/register/local', methods=['POST'])
def register_from_local():
    definition_file = request.files.get("definition")
    binary = request.files.get("binary")
    if not all([definition_file, binary]):
        return param_error(msg="definition and binary cannot be empty")
    definition = get_definition(definition_file.read())
    plugin_manager.register(definition, binary.read())
    return success()


@plugin_blu.route("/<plugin_name>", methods=['DELETE'])
def unregister_plugin_handler(plugin_name):
    plugin_manager.unregister(plugin_name)
    return success()
