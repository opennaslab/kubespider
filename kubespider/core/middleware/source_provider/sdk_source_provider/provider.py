import fcntl
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
    def __init__(self, name: str, bin_path: str, pid=None, **params) -> None:
        self.name = name
        self.bin_path = bin_path
        self.params = params
        self.is_active = False
        self.pid = pid
        self.host = None
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
            self.host = kwargs.get("host")
            self.apis = kwargs.get("api")
            self.is_active = True
            logging.info(f"[SdkSourceProvider:%s] active success.", self.name)
        except Exception as err:
            logging.error(f"[SdkSourceProvider:%s] active failed: %s", self.name, err)
        return self.is_active

    def prepare_command(self):
        command = [
            self.bin_path,
            f"--ks_host=http://127.0.0.1:{Config.SERVER_PORT}",
            f"--ks_proxy={Config.PROXY or ''}",
            f"--ks_pid={self.pid}"
        ]
        for key, value in self.params.items():
            if isinstance(value, bool) or value is None:
                value = "true" if value else ""
            command.append(f"--{key}={value}")
        return command

    def run_binary(self):
        process = subprocess.Popen(self.prepare_command(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for pipe in [process.stdout, process.stderr]:
            fd = pipe.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        return process

    def kill(self):
        if self.process:
            self.process.kill()

    def is_alive(self):
        try:
            resp = requests.post(self.host, json={"api": SourceProviderApi.health}).json()
            if resp.get("code") == 200:
                return True
            return False
        except Exception as err:
            logging.error("[SdkSourceProvider:%s] has gone, error:%s", err)
            return False

    def search(self, sync=False, **kwargs) -> dict:
        if SourceProviderApi.search not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.host, json={
                "api": SourceProviderApi.search,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()

    def schedule(self, sync=False, **kwargs) -> dict:
        if SourceProviderApi.schedule not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.host, json={
                "api": SourceProviderApi.schedule,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()

    def handler(self, sync=True, **kwargs) -> dict:
        if SourceProviderApi.handler not in self.apis:
            func_name = inspect.currentframe().f_code.co_name
            raise UnSupportedMethod(self, func_name)
        else:
            resp = requests.post(self.host, json={
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
            resp = requests.post(self.host, json={
                "api": SourceProviderApi.document,
                "sync": sync,
                "data": kwargs
            })
            return resp.json()
