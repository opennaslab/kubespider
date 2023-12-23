import _thread
import argparse
import logging
import sys
import traceback
import requests
import yaml
import json
from urllib.parse import urljoin
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from .tools import get_request_controller
from .data_types import ParamType, ProviderInstanceType, HttpApi

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')


class SDKHTTPRequestHandler(BaseHTTPRequestHandler):
    PROVIDER = None
    PROVIDER_KWARGS = None
    PROVIDER_INSTANCE = None
    PROVIDER_INSTANCE_TYPE = None
    KS_PROXY = None
    KS_HOST = None
    APIS = {}

    def do_GET(self):
        self._set_response(dict(code=400, msg="UnSupport Get Method"))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            result = self.call_api(json.loads(post_data))
            self._set_response(result)
        except Exception as err:
            logging.error(traceback.format_exc())
            self._set_response({
                "code": 500,
                "msg": "Request Failed",
                "traceback": str(err)
            })

    def _set_response(self, data: dict) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def call_api(self, post_data):
        sync = post_data.get("sync", True)
        data = post_data.get("data", {})
        success, method, response = self.validate_request(post_data)
        if not success:
            return response
        else:
            if sync:
                return {
                    "code": 200,
                    "msg": "ok",
                    "data": method(**data)
                }
            else:
                _thread.start_new_thread(lambda: self.call_api_asyncio(method, data), ())
                return {
                    "code": 200,
                    "msg": "ok",
                    "data": None
                }

    @classmethod
    def call_api_asyncio(cls, method, data):
        result = method(**data)
        KubespiderClient(cls.KS_HOST).receive_resource(result)

    def validate_request(self, post_data):
        api = post_data.get("api")
        sync = post_data.get("sync", True)
        success = True
        method = None
        response = {}
        if sync is False and api not in HttpApi.async_api_support():
            success = False
            response = {
                "code": 400,
                "msg": f"{api} does not support async"
            }
            return success, method, response
        if api not in self.APIS.keys():
            success = False
            response = {
                "code": 400,
                "msg": "Api not exist"
            }
            return success, method, response
        method = self.get_method_for_api(api)
        if not method:
            success = False
            response = {
                "code": 400,
                "msg": f"{self.PROVIDER} does not support api: {api}"
            }
        return success, method, response

    def get_method_for_api(self, api):
        if self.PROVIDER_INSTANCE_TYPE == ProviderInstanceType.single:
            if not self.PROVIDER_INSTANCE:
                self.PROVIDER_INSTANCE = self.PROVIDER(
                    request_handler=partial(get_request_controller, self.KS_PROXY),
                    **self.PROVIDER_KWARGS)
            method = getattr(self.PROVIDER_INSTANCE, self.APIS[api], None)
        else:
            provider_instance = self.PROVIDER(
                request_handler=partial(get_request_controller, self.KS_PROXY),
                **self.PROVIDER_KWARGS)
            method = getattr(provider_instance, self.APIS[api], None)
        return method

    @classmethod
    def path_registry(cls, obj, api):
        function_name = obj.__name__
        cls.APIS[api] = function_name


class KubespiderClient:
    def __init__(self, host):
        self.host = host

    def instance_reply(self, ks_pid, server_port) -> bool:
        try:
            url = urljoin(self.host, "/api/v2/provider/source/instance/reply")
            data = {
                "pid": ks_pid,
                "host": f"http://127.0.0.1:{server_port}",
                "api": list(SDKHTTPRequestHandler.APIS.keys())
            }
            logging.info("[%s] reply data: %s", SDKHTTPRequestHandler.PROVIDER.__name__, data)
            resp = requests.post(url, json=data).json()
            if resp.get("code") == 200:
                logging.info("[%s] reply to kubespider success", SDKHTTPRequestHandler.PROVIDER.__name__)
                return True
            else:
                logging.error("[%s] reply to kubespider failed: %s", SDKHTTPRequestHandler.PROVIDER.__name__, resp)
                return False
        except Exception as err:
            logging.error("[%s] reply to kubespider failed: %s", SDKHTTPRequestHandler.PROVIDER.__name__, err)
            return False

    def receive_resource(self, resources: list[dict]):
        try:
            url = urljoin(self.host, "/api/v2/resource/receive")
            data = {
                "resources": resources,
            }
            resp = requests.post(url, json=data).json()
            logging.info("[%s] kubespider receive resource success", SDKHTTPRequestHandler.PROVIDER.__name__, resp)
        except Exception as err:
            logging.error("[%s] kubespider receive resource failed: %s", SDKHTTPRequestHandler.PROVIDER.__name__, err)


class Manager:

    def __init__(self, provider_instance_type=ProviderInstanceType.multi):
        self.provider_instance_type = provider_instance_type
        self.http_server = None

    @staticmethod
    def extract_parameters(parameters):
        params = parameters.get("instance_params", [])
        provider_type = parameters.get("provider_type")
        provider_name = parameters.get("provider_name")
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=f"Kubespider [{provider_type} : {provider_name}] ",
            prog='kubespider'
        )
        for param in params:
            param_type = getattr(ParamType, param.get('value_type', ""))
            parser.add_argument(
                f"--{param.get('name')}",
                type=param_type,
                help=param.get('desc'),
                nargs='+' if param_type == list else '?'
            )
        parser.add_argument(
            "--get_document",
            type=bool,
            help="get provider document without start http service",
            nargs='?'
        )
        parser.add_argument(
            "--cache_path",
            type=str,
            help="the path to save the provider`s cache")
        parser.add_argument(
            "--ks_host",
            type=str,
            help="kubespider`s host")
        parser.add_argument(
            "--ks_pid",
            type=int,
            help="kubespider`s source provider instance id")
        parser.add_argument(
            "--ks_proxy",
            type=str,
            help="kubespider`s request handler proxy")
        namespace = parser.parse_args()
        kwargs = vars(namespace)
        return kwargs

    def run(self):
        parameters = self._document()
        kwargs = self.extract_parameters(parameters)
        if kwargs.get("get_document") is True:
            print(json.dumps(parameters))
            return
        kwargs.pop("get_document", None)
        ks_host = kwargs.pop("ks_host", "")
        ks_pid = kwargs.pop("ks_pid", "")
        ks_proxy = kwargs.pop("ks_proxy", "")
        logging.info(f"params: {kwargs}")
        SDKHTTPRequestHandler.PROVIDER_INSTANCE_TYPE = self.provider_instance_type
        SDKHTTPRequestHandler.PROVIDER_KWARGS = kwargs
        SDKHTTPRequestHandler.KS_PROXY = ks_proxy
        SDKHTTPRequestHandler.KS_HOST = ks_host
        if all([
            SDKHTTPRequestHandler.PROVIDER,
            SDKHTTPRequestHandler.PROVIDER_KWARGS,
            SDKHTTPRequestHandler.PROVIDER_INSTANCE_TYPE,
        ]):
            self.http_server = HTTPServer(("", 0), SDKHTTPRequestHandler)
            if self.provider_instance_type == ProviderInstanceType.single:
                SDKHTTPRequestHandler.PROVIDER_INSTANCE = SDKHTTPRequestHandler.PROVIDER(
                    request_handler=partial(get_request_controller, ks_proxy),
                    **kwargs
                )
            KubespiderClient(ks_host).instance_reply(ks_pid, self.http_server.server_port)
            self.http_server.serve_forever()
        else:
            logging.error(f"[{SDKHTTPRequestHandler.PROVIDER}] Start failed")

    @staticmethod
    def _document(*args):
        base_path = getattr(sys, '_MEIPASS', None)
        if not base_path:
            base_path = '.'
        with open(f'{base_path}/provider.yaml') as f:
            conf = f.read()
            data = yaml.safe_load(conf)
            return data

    @staticmethod
    def registry(api):
        def wrapper(func):
            SDKHTTPRequestHandler.path_registry(func, api)
            return func

        return wrapper

    @classmethod
    def registry_doc(cls, provider_class):
        setattr(provider_class, "_document", cls._document)
        cls.registry(HttpApi.document)(cls._document)

    @classmethod
    def registry_health(cls, provider_class):
        def _health(*args, **kwargs):
            return

        setattr(provider_class, "_health", _health)
        cls.registry(HttpApi.health)(_health)

    def __call__(self, provider_class):
        if not SDKHTTPRequestHandler.PROVIDER:
            SDKHTTPRequestHandler.PROVIDER = provider_class
            self.registry_doc(provider_class)
            self.registry_health(provider_class)
        else:
            raise Exception(f'This manager has been bound on <{SDKHTTPRequestHandler.PROVIDER}>')

        return provider_class
