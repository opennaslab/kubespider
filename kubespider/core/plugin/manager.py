import os
import time
import subprocess
import _thread
import logging
import signal

from models import session_context
from models.models import Plugin, Binding

from plugin_provider.parser import ParserProvider
from plugin_provider.search import SearchProvider
from plugin_provider.scheduler import SchedulerProvider
from utils.definition import Definition
from utils.global_config import APPConfig
from utils.types import ProviderTypes, PluginTypes
from utils.values import CFG_BASE_PATH
from utils import helper

PLUGIN_BASE_PATH = CFG_BASE_PATH + "plugins/"
PLUGIN_BINARY_PATH = PLUGIN_BASE_PATH + "binaries/"


class PluginInstance:
    def __init__(self, definition: Definition):
        self.definition = definition
        self.request = helper.get_request_controller()
        self.process = None
        self.port = 0

    def enable(self):
        if self.port:
            up = self.__health()
            if up:
                return
        binary = PLUGIN_BINARY_PATH + self.definition.name
        if not os.path.exists(binary):
            self.__download_binary()

        self.port = helper.get_free_port()
        # start the plugin
        command = f"{binary} --name={self.definition.name} --port={self.port} --proxy={APPConfig.PROXY or ''}"
        self.process = subprocess.Popen(command, shell=True)
        _thread.start_new_thread(self.__run_plugin, ())
        # wait for the plugin to start
        for _ in range(10):
            if self.__health():
                logging.info('[PluginManager] Plugin started: %s', self.definition.name)
                return
            time.sleep(2)
            logging.info('[PluginManager] connect to Plugin : %s ...', self.definition.name)
        raise Exception(f"[PluginManager] Failed to start plugin: {self.definition.name}")

    def disable(self):
        if not self.process:
            return
        logging.info('[PluginManager] Stopping plugin: %s', self.definition.name)
        self.process.send_signal(signal.SIGTERM)

    def __health(self) -> bool:
        try:
            self.call_api("_health", timeout=2)
            return True
        except Exception:
            return False

    def call_api(self, api: str, timeout=30, **kwargs) -> dict:
        if not self.port:
            raise Exception("Plugin not enabled")
        body = {"api": api, **kwargs}
        response = self.request.post(url=f"http://localhost:{self.port}", json=body, timeout=timeout)
        if response.status_code != 200:
            raise Exception(f"Failed to call plugin API: {api}")
        json = response.json()
        if json.get("code") != 200:
            raise Exception(f"Failed to call plugin API: {api}, {json.get('msg')}")

        return json

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


class PluginManager:
    def __init__(self):

        self.definitions: dict[str, Definition] = {}
        self.instances: dict[str, PluginInstance] = {}
        self.request = helper.get_request_controller()

    def list_plugin(self) -> list[Definition]:
        return list(self.definitions.values())

    def list_instance(self) -> list[PluginInstance]:
        return list(self.instances.values())

    def get_plugin(self, plugin_name: str) -> Definition:
        return self.definitions.get(plugin_name)

    def get_instance(self, plugin_name: str) -> PluginInstance:
        return self.instances.get(plugin_name)

    def load_local(self) -> None:
        with session_context() as session:
            # Load the plugin definitions
            for plugin in session.query(Plugin).all():
                definition = Definition.init_from_dict(**plugin.serializer())
                self.definitions[definition.name] = definition
                if plugin.enable:
                    definition = Definition.init_from_dict(**plugin.serializer())
                    instance = PluginInstance(definition)
                    instance.enable()
                    self.instances[plugin.name] = instance
                    logging.info('[PluginManager] Restore plugin instance: %s', definition.name)
                else:
                    logging.info('[PluginManager] Plugin %s not enabled', definition.name)

    def register(self, definition: Definition, binary: bytes = None):
        with session_context() as session:
            # Save the plugin binary
            if binary:
                binary_file = PLUGIN_BINARY_PATH + definition.name
                if os.path.exists(binary_file):
                    os.remove(binary_file)
                # Save the binary
                with open(binary_file, "wb") as file:
                    file.write(binary)
                # Make the binary executable
                os.chmod(binary_file, 0o755)
            # Save the plugin definition
            definition_dict = definition.serializer()
            plugin = session.query(Plugin).filter_by(name=definition.name).first() or Plugin()
            plugin.name = definition_dict.get("name")
            plugin.version = definition_dict.get("version")
            plugin.author = definition_dict.get("author")
            plugin.type = definition_dict.get("type")
            plugin.description = definition_dict.get("description")
            plugin.language = definition_dict.get("language")
            plugin.logo = definition_dict.get("logo")
            plugin.binary = definition_dict.get("binary")
            plugin.arguments = definition_dict.get("arguments")
            session.add(plugin)
            session.commit()
            if self.instances.get(plugin.name):
                instance = self.instances.get(plugin.name)
                if not instance:
                    # Just ignore re-disable plugin operation
                    return
                instance.disable()
                del self.instances[plugin.name]
            self.definitions[definition.name] = definition
            logging.info('Plugin %s registered', plugin.name)

    def unregister(self, plugin: [str, Plugin]):
        with session_context() as session:
            if isinstance(plugin, str):
                plugin = session.query(Plugin).filter_by(name=plugin).first()
            configs = plugin_binding.list_config()
            for config in configs:
                if config.plugin.id == plugin.id:
                    raise Exception(
                        f'Plugin {plugin.name} is used by {config.name} currently, please delete it first...')
            definition = self.definitions.get(plugin.name)
            if not definition:
                raise Exception(f"Plugin not found: {plugin.name}")
            # Disable the plugin if it is enabled
            if self.instances.get(plugin.name):
                self.disable(plugin)
            # Remove the plugin definition and binary
            try:
                del self.definitions[plugin.name]
                os.remove(PLUGIN_BINARY_PATH + plugin.name)
            except FileNotFoundError:
                pass
            session.delete(plugin)
            session.commit()
            logging.info('Plugin %s unregister', plugin.name)

    def enable(self, plugin: [str, Plugin]):
        with session_context() as session:
            if isinstance(plugin, str):
                plugin = session.query(Plugin).filter_by(name=plugin).first()
            if not plugin:
                raise Exception("Plugin not found")
            if self.instances.get(plugin.name):
                # Just ignore re-enable plugin operation
                return
            plugin.enable = True
            session.add(plugin)
            session.commit()
            definition = Definition.init_from_dict(**plugin.serializer())
            instance = PluginInstance(definition)
            instance.enable()
            self.instances[plugin.name] = instance

    def disable(self, plugin: [str, Plugin]):
        with session_context() as session:
            if isinstance(plugin, str):
                plugin = session.query(Plugin).filter_by(name=plugin).first()
            if not plugin:
                raise Exception("Plugin not found")
            instance = self.instances.get(plugin.name)
            if not instance:
                # Just ignore re-disable plugin operation
                return
            instance.disable()
            del self.instances[plugin.name]
            plugin.enable = False
            session.add(plugin)
            session.commit()

    def call(self, plugin_name: str, api_name: str, **kwargs) -> dict:
        instance = self.instances.get(plugin_name)
        if not instance:
            raise Exception(f"Plugin not enabled: {plugin_name}")
        return instance.call_api(api_name, **kwargs)

    def provider_maker(self, bind, provider_type=None):
        bind_type = bind.type
        plugin_instance = self.get_instance(bind.plugin.name)
        provider = None
        if not plugin_instance:
            logging.warning("[PluginManager] Plugin: %s has gone", bind.plugin.name)
            return provider
        if provider_type == ProviderTypes.scheduler and bind_type == PluginTypes.scheduler:
            provider = self.__make_scheduler_provider(bind_type, plugin_instance)
        elif provider_type == ProviderTypes.search and bind_type in [PluginTypes.search, PluginTypes.scheduler]:
            provider = self.__make_search_provider(bind, plugin_instance)
        elif provider_type == ProviderTypes.parser and bind_type in PluginTypes.types():
            provider = self.__make_parser_provider(bind, plugin_instance)
        return provider

    @staticmethod
    def __make_parser_provider(bind, plugin_instance):
        plugin_name = bind.plugin.name
        provider_cls = type(f"{plugin_name}ParserProvider", (ParserProvider,), {})
        return provider_cls(bind, plugin_instance)

    @staticmethod
    def __make_search_provider(bind, plugin_instance):
        plugin_name = bind.plugin.name
        provider_cls = type(f"{plugin_name}SearchProvider", (SearchProvider,), {})
        return provider_cls(bind, plugin_instance)

    @staticmethod
    def __make_scheduler_provider(bind, plugin_instance):
        plugin_name = bind.plugin.name
        provider_cls = type(f"{plugin_name}PeriodProvider", (SchedulerProvider,), {})
        return provider_cls(bind, plugin_instance)


class PluginBinding:
    @staticmethod
    def list_config(config_type: str = None, ids: list = None) -> list[Binding]:
        with session_context() as session:
            query = session.query(Binding)
            if config_type:
                query = query.filter_by(type=config_type)
            if ids:
                query = query.filter(Binding.id.in_(ids))
            return query.all()

    def create_or_update(self, **config_data: dict) -> None:
        with session_context() as session:
            _id = config_data.pop('id', None)
            name = config_data.pop('name', "")
            config_type = config_data.pop('type')
            plugin_name = config_data.pop('plugin_name')
            plugin = session.query(Plugin).filter_by(name=plugin_name).first()
            if not all([name, config_type, plugin_name]):
                raise Exception('name and plugin_name are required')
            bind_model = session.query(Binding).filter_by(id=_id).first() or Binding()
            bind_model.name = name
            bind_model.type = config_type
            bind_model.plugin_id = plugin.id
            bind_model.plugin = plugin
            bind_model.arguments = config_data
            self.__validate(bind_model)
            session.add(bind_model)
            session.commit()

    @staticmethod
    def remove(_id: int) -> None:
        with session_context() as session:
            config_model = session.query(Binding).filter_by(id=_id).first()
            if config_model:
                session.delete(config_model)
                session.commit()

    @staticmethod
    def __validate(config: Binding):
        plugin_definition = plugin_manager.get_plugin(config.plugin.name)
        if not plugin_definition:
            raise Exception('plugin not found')
        plugin_definition.validate(**config.arguments)


plugin_manager: PluginManager = PluginManager()
plugin_binding: PluginBinding = PluginBinding()
