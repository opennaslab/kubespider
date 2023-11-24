import argparse
import logging
import sys
import traceback

import requests
import yaml
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from .tools import get_request_controller
from functools import partial

from .data_types import ParamType, ProviderInstanceType, HttpApi

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')


class SDKHTTPRequestHandler(BaseHTTPRequestHandler):
    PROVIDER = None
    PROVIDER_KWARGS = None
    PROVIDER_INSTANCE = None
    PROVIDER_INSTANCE_TYPE = None
    PROXY = None
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
        api = post_data.get("api")
        # todo async run
        sync = post_data.get("sync", True)
        data = post_data.get("data", {})
        if api not in self.APIS.keys():
            return {
                "code": 400,
                "msg": "Api Not Exist"
            }
        else:
            if not self.PROVIDER_INSTANCE and self.PROVIDER_INSTANCE_TYPE == ProviderInstanceType.single:
                data = getattr(self.PROVIDER_INSTANCE, api)(**data)
            else:
                data = getattr(self.PROVIDER(
                    request_handler=partial(get_request_controller, self.PROXY),
                    **self.PROVIDER_KWARGS),
                    self.APIS[api]
                )(**data)

            return {
                "code": 200,
                "msg": "ok",
                "data": data
            }

    @classmethod
    def path_registry(cls, obj, api):
        function_name = obj.__name__
        cls.APIS[api] = function_name


class Manager:

    def __init__(self, provider_instance_type=ProviderInstanceType.multi):
        self.provider_instance_type = provider_instance_type
        self.http_server = None

    def run(self):
        parameters = self.document()
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
            "--ks_uid",
            type=str,
            help="kubespider`s source provider instance uid")
        parser.add_argument(
            "--ks_proxy",
            type=str,
            help="kubespider`s request handler proxy")
        namespace = parser.parse_args()
        kwargs = vars(namespace)
        if kwargs.get("get_document") is True:
            print(json.dumps(parameters))
            return
        kwargs.pop("get_document", None)
        ks_uri = kwargs.pop("ks_host", "")
        ks_uid = kwargs.pop("ks_uid", "")
        kubespider_proxy = kwargs.pop("ks_proxy", "")
        logging.info(f"params: {kwargs}")
        SDKHTTPRequestHandler.PROVIDER_INSTANCE_TYPE = self.provider_instance_type
        SDKHTTPRequestHandler.PROVIDER_KWARGS = kwargs
        SDKHTTPRequestHandler.PROXY = kubespider_proxy
        if all([
            SDKHTTPRequestHandler.PROVIDER,
            SDKHTTPRequestHandler.PROVIDER_KWARGS,
            SDKHTTPRequestHandler.PROVIDER_INSTANCE_TYPE,
        ]):
            self.http_server = HTTPServer(("", 0), SDKHTTPRequestHandler)
            if self.provider_instance_type == ProviderInstanceType.single:
                SDKHTTPRequestHandler.PROVIDER_INSTANCE = SDKHTTPRequestHandler.PROVIDER(
                    request_handler=partial(get_request_controller, kubespider_proxy),
                    **kwargs
                )
            success = self.reply_to_ks(ks_uid, ks_uri)
            if success:
                logging.info(f"[{SDKHTTPRequestHandler.PROVIDER}] Start success")
            self.http_server.serve_forever()
        else:
            logging.error(f"[{SDKHTTPRequestHandler.PROVIDER}] Start failed")

    def reply_to_ks(self, ks_uid, ks_uri):
        try:
            data = {
                "uid": ks_uid,
                "uri": f"http://127.0.0.1:{self.http_server.server_port}",
                "api": list(SDKHTTPRequestHandler.APIS.keys())
            }
            logging.info(f"Reply Data: {data}")
            resp = requests.post(ks_uri, json=data).json()
            if resp.get("code") == 200:
                logging.info(f"[{SDKHTTPRequestHandler.PROVIDER}] Reply to kubespider success")
                return True
            else:
                logging.info(f"[{SDKHTTPRequestHandler.PROVIDER}] Reply to kubespider failed: {resp}")
                return False
        except Exception as err:
            logging.error(f"[{SDKHTTPRequestHandler.PROVIDER}] Reply to kubespider failed: {err}")
            return False

    @staticmethod
    def document(*args):
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

            def handler(*args, **kwargs):
                return func(*args, **kwargs)

            return handler

        return wrapper

    @classmethod
    def registry_doc(cls, provider_class):
        setattr(provider_class, "document", cls.document)
        cls.registry(HttpApi.document)(cls.document)

    def __call__(self, provider_class):
        if not SDKHTTPRequestHandler.PROVIDER:
            SDKHTTPRequestHandler.PROVIDER = provider_class
            self.registry_doc(provider_class)
        else:
            raise Exception(f'This manager has been bound on <{SDKHTTPRequestHandler.PROVIDER}>')

        return provider_class
