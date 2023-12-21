import inspect
import json
import logging
import os
import subprocess
import requests

from core.exceptions import UnSupportedMethod
from core.middleware.source_provider.provider import SourceProvider
from utils import values
from utils.global_config import Config
from utils.values import SourceProviderApi


class SdkSourceProvider(SourceProvider):
    def __init__(self, name: str, bin_path: str, **kwargs) -> None:
        self.name = name
        self.bin_path = bin_path
        self.params = kwargs
        self.is_active = False
        self.c_pid = None
        self.uri = None
        self.apis = []
        self.process = self.run_binary()

    @staticmethod
    def spec():
        binary_path = values.Config.SOURCE_PROVIDERS_BIN.config_path()
        binaries = [os.path.join(binary_path, b) for b in os.listdir(binary_path)]
        specs = []
        for binary in binaries:
            spec = None
            try:
                cmd = [binary, "--get_document", "true"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                l_result = [line for line in result.stdout.split('\n') if line.strip()]
                spec = json.loads(l_result[-1])
                spec["bin"] = binary
                specs.append(spec)
            except Exception as err:
                logging.error("[SdkSourceProvider] get %s spec failed, spec: %s, err: %s", binary, spec, err)
        return specs

    def active(self, **kwargs):
        try:
            self.uri = kwargs.get("uri")
            self.apis = kwargs.get("api")
            self.is_active = True
            logging.info(f"[SdkSourceProvider:%s] active success.", self.name)
        except Exception as err:
            logging.error(f"[SdkSourceProvider:%s] active failed: %s", self.name, err)
        return self.is_active

    def prepare_command(self):
        command = [
            self.bin_path,
            f"--ks_host=http://127.0.0.1:{Config.SERVER_PORT}/api/v2/provider/source/instance/reply",
            f"--ks_proxy={Config.PROXY}",
            f"--ks_uid={1}"
        ]
        for key, value in self.params.items():
            command.append(f"--{key}={value}")
        return command

    def run_binary(self):
        return subprocess.Popen(self.prepare_command(), stdout=open('output.log', 'w'), stderr=open('error.log', 'w'))

    def kill(self):
        if self.process:
            self.process.kill()

    def is_alive(self):
        try:
            if self.process.poll() is not None:
                return True
        except Exception as err:
            logging.error("[SdkSourceProvider:%s] has gone, error:%s", err)
            return False

    def search(self, sync=False, **kwargs) -> list:
        if SourceProviderApi.search not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.uri, json={
                "api": SourceProviderApi.search,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()

    def schedule(self, sync=False, **kwargs) -> bool:
        if SourceProviderApi.schedule not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.uri, json={
                "api": SourceProviderApi.schedule,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()

    def handler(self, sync=True, **kwargs) -> list:
        if SourceProviderApi.handler not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.uri, json={
                "api": SourceProviderApi.handler,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()

    def document(self, sync=True, **kwargs) -> dict:
        if SourceProviderApi.document not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.uri, json={
                "api": SourceProviderApi.document,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()
