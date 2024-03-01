import os
import time
import subprocess
import _thread
import logging
import signal
import shutil

from utils.values import CFG_BASE_PATH, Resource
from utils.config_reader import YamlFileConfigReader, YamlFileSectionConfigReader
from utils import helper

PLUGIN_BASE_PATH = CFG_BASE_PATH + "plugins/"
PLUGIN_DEFINITION_PATH = PLUGIN_BASE_PATH + "definitions/"
PLUGIN_BINARY_PATH = PLUGIN_BASE_PATH + "binaries/"
PLUGIN_STATE_PATH = PLUGIN_BASE_PATH + "state.yaml"


class PluginConfigDefinition:

    def __init__(self, name: str, field_type: str, description: str, placeholder: str, required: bool, default: any):
        self.name = name
        self.type = field_type
        self.description = description
        self.placeholder = placeholder
        self.required = required
        self.default = default

    def __str__(self) -> str:
        return f"PluginConfigDefinition(name: {self.name}, type: {self.type}, \
            description: {self.description}, placeholder: {self.placeholder}, \
                required: {self.required}, default: {self.default})"


class PluginDefinition:

    def __init__(self, yaml_file: str):
        reader = YamlFileConfigReader(yaml_file)
        yaml_data = reader.read()
        self.name = yaml_data.get("name")
        self.version = yaml_data.get("version")
        self.author = yaml_data.get("author")
        self.type = yaml_data.get("type")
        self.description = yaml_data.get("description")
        self.language = yaml_data.get("language")
        self.logo = yaml_data.get("logo")
        self.binary = yaml_data.get("binary")
        self.arguments = []
        if yaml_data.get("arguments"):
            self.arguments = [PluginConfigDefinition(
                **item) for item in yaml_data["arguments"]]

    def validate(self, config: dict) -> bool:
        if not self.arguments:
            return True
        for arg in self.arguments:
            # Check if the argument is required
            if arg.required and not config.get(arg.name):
                return False
            # Check if the argument type is correct
            if config.get(arg.name) and self.__check_type(config.get(arg.name), arg.type) is False:
                return False

        return True

    def __check_type(self, value: any, field_type: str) -> bool:
        if field_type == "text":
            return isinstance(value, str)
        if field_type == "number":
            return isinstance(value, (int, float))
        if field_type == "boolean":
            return isinstance(value, bool)
        if field_type == "list":
            return isinstance(value, list)
        if field_type == "dict":
            return isinstance(value, dict)
        return False

    def __str__(self) -> str:
        return f"PluginDefinition(name: {self.name}, \
        version: {self.version}, author: {self.author}, \
        type: {self.type}, description: {self.description}, \
        language: {self.language}, logo: {self.logo}, \
        binary: {self.binary}, arguments: {self.arguments})"

    def to_dict(self) -> dict:
        data = {}
        data.update(self.__dict__)
        if self.arguments:
            data["arguments"] = [item.__dict__ for item in self.arguments]
        return data


class PluginInstance:
    def __init__(self, definition: PluginDefinition, state_reader: YamlFileConfigReader):
        self.definition = definition
        self.reader = state_reader
        self.state = state_reader.read()
        self.request = helper.get_request_controller()
        self.process = None

    def enable(self):
        port = self.state.get("port")
        if port:
            up = self.__helath()
            if up:
                return
        binary = PLUGIN_BINARY_PATH + self.definition.name
        if not os.path.exists(binary):
            self.__download_binary()

        plugin_port = helper.get_free_port()
        # start the plugin
        command = f"{binary} --name {self.definition.name} --port {plugin_port}"
        self.process = subprocess.Popen(command, shell=True)
        _thread.start_new_thread(self.__run_plugin, ())
        self.__update_state("port", plugin_port)
        # wait for the plugin to start
        for _ in range(5):
            if self.__helath():
                logging.info('Plugin started: %s', self.definition.name)
                return
            time.sleep(2)
        self.__update_state("port", None)
        raise Exception(f"Failed to start plugin: {self.definition.name}")

    def disable(self):
        self.__update_state("port", None)
        if not self.process:
            return
        logging.info('Stopping plugin: %s', self.definition.name)
        self.process.send_signal(signal.SIGTERM)

    def __helath(self) -> bool:
        try:
            self.call_api("_health")
            return True
        except Exception as e:
            logging.error('Plugin health check failed: %s', e)
            return False

    def call_api(self, api: str, **kwargs):
        port = self.state.get("port")
        if not port:
            raise Exception("Plugin not enabled")
        body = {
            "api": api,
            **kwargs
        }
        response = self.request.post(
            url=f"http://localhost:{port}", json=body, timeout=1)
        if response.status_code != 200:
            raise Exception(
                f"Failed to call plugin API: {api}")
        json = response.json()
        if json.get("code") != 200:
            raise Exception(
                f"Failed to call plugin API: {api}, {json.get('msg')}")

        return json.get("data")

    def __run_plugin(self):
        self.process.wait()

    def __download_binary(self):
        if not self.definition.binary:
            return
        if not os.path.exists(PLUGIN_BINARY_PATH):
            os.makedirs(PLUGIN_BINARY_PATH)
        # Download the binary
        response = self.request.get(self.definition.binary, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download plugin binary: {self.definition.binary}")
        # When the binary exists, remove it
        binary_file = PLUGIN_BINARY_PATH + self.definition.name
        if os.path.exists(binary_file):
            os.remove(binary_file)
        # Save the binary
        with open(binary_file, "wb") as file:
            file.write(response.content)
        # Make the binary executable
        os.chmod(binary_file, 0o755)

    def __update_state(self, key: str, value: str):
        self.state[key] = value
        self.reader.save(self.state)


class PluginManager:
    def __init__(self):
        self.definitions: dict[str, PluginDefinition] = {}
        self.instances: dict[str, PluginInstance] = {}
        self.request = helper.get_request_controller()
        self.state = YamlFileConfigReader(PLUGIN_STATE_PATH).read()

    def list_plugin(self) -> list[PluginDefinition]:
        return self.definitions.values()

    def get_plugin(self, plugin_name: str) -> PluginDefinition:
        return self.definitions.get(plugin_name)

    def load_local(self) -> None:
        if not os.path.exists(PLUGIN_DEFINITION_PATH):
            os.makedirs(PLUGIN_DEFINITION_PATH)
            return
        # Load the plugin definitions
        for file in os.listdir(PLUGIN_DEFINITION_PATH):
            if file.endswith(".yaml"):
                logging.info('Loading plugin definition: %s', file)
                definition = PluginDefinition(
                    PLUGIN_DEFINITION_PATH + file)
                self.definitions[definition.name] = definition
        # Auto enable when the state exists
        for definition in self.definitions.values():
            if self.state.get(definition.name) and self.state[definition.name].get("port", None):
                logging.info('Restore plugin instance: %s', definition.name)
                reader = YamlFileSectionConfigReader(
                    PLUGIN_STATE_PATH, definition.name)
                instance = PluginInstance(
                    definition, reader)
                instance.enable()
                self.instances[definition.name] = instance

    def register(self, yaml_file: str):
        # Download the plugin definition
        response = self.request.get(yaml_file, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download plugin definition: {yaml_file}")

        tmp_file = helper.get_tmp_file_name(yaml_file)
        with open(tmp_file, "wb") as file:
            file.write(response.content)
        # Read the plugin definition
        definition = PluginDefinition(tmp_file)
        # Check if the plugin definition already exists
        exists = self.definitions.get(definition.name)
        if exists:
            raise Exception(
                f"Plugin definition already exists: {definition.name}")
        # Save the plugin definition
        shutil.move(tmp_file, PLUGIN_DEFINITION_PATH + definition.name +
                    ".yaml")
        self.definitions[definition.name] = definition

    def unregister(self, plugin_name: str):
        definition = self.definitions.get(plugin_name)
        if not definition:
            raise Exception(f"Plugin not found: {plugin_name}")
        reader = YamlFileConfigReader(PLUGIN_STATE_PATH)
        self.state = reader.read()
        del self.definitions[plugin_name]
        del self.instances[plugin_name]
        if self.state.get(plugin_name):
            del self.state[plugin_name]
            reader.save(self.state)
        os.remove(PLUGIN_DEFINITION_PATH + plugin_name + ".yaml")
        os.remove(PLUGIN_BINARY_PATH + plugin_name)

    def enable(self, plugin_name: str):
        definition = self.definitions.get(plugin_name)
        if not definition:
            raise Exception(f"Plugin not found: {plugin_name}")
        instance = PluginInstance(
            definition, YamlFileSectionConfigReader(PLUGIN_STATE_PATH, plugin_name))
        instance.enable()
        self.instances[plugin_name] = instance

    def disable(self, plugin_name: str):
        instance = self.instances.get(plugin_name)
        if not instance:
            raise Exception(f"Plugin not enabled: {plugin_name}")
        reader = YamlFileConfigReader(PLUGIN_STATE_PATH)
        self.state = reader.read()
        instance.disable()
        del self.instances[plugin_name]
        if self.state.get(plugin_name):
            del self.state[plugin_name]
            reader.save(self.state)

    def call(self, plugin_name: str, api_name: str, **kwargs) -> list[Resource]:
        instance = self.instances.get(plugin_name)
        if not instance:
            raise Exception(f"Plugin not enabled: {plugin_name}")
        return instance.call_api(api_name, **kwargs)


kubespider_plugin_manager: PluginManager = None
