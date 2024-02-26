from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import argparse
import logging
import traceback

from kubespider_source_provider_sdk.values import ProviderType


class SDKHTTPRequestHandler(BaseHTTPRequestHandler):

    PROVIDER = None
    API = {}

    # pylint: disable=redefined-builtin
    def log_message(self, format: str, *args) -> None:
        return

    # pylint: disable=invalid-name
    def do_GET(self) -> None:
        self.__send_response({
            "code": 400,
            "msg": "GET method not supported"
        })

    def do_POST(self) -> None:
        # Get the content length
        content_length = int(self.headers["Content-Length"])
        # Read the data from the request
        data = self.rfile.read(content_length).decode("utf-8")
        # Parse the data as a JSON object
        data = json.loads(data)
        try:
            # Call the API
            response = self.__call_api(data)
            # Send the response
            self.__send_response({
                "code": 200,
                "msg": "Success",
                "data": response
            })
        except Exception as e:
            logging.error('Calling API failed: %s', traceback.format_exc())
            self.__send_response({
                "code": 500,
                "msg": str(e)
            })

    @classmethod
    def register(cls, func, api: str) -> None:
        cls.API[api] = func

    def __call_api(self, data: dict):

        api = data.pop("api", None)
        if not api:
            raise Exception("API not found")

        if api not in self.API:
            raise Exception(f"API <{api}> not found")

        logging.info('Calling API <%s>', api)

        return self.API[api](**data)

    def __send_response(self, response: dict) -> None:
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


class SDK:

    def __init__(self, provider_type: ProviderType) -> None:
        self.__http_server = None
        self.__type = provider_type

    def __run(self) -> None:
        params = self.__extract_params()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s-%(levelname)s: [' + params['name'] + '] %(message)s')
        logging.info('Running the provider on port <%s>', params['port'])
        self.__http_server = HTTPServer(
            ("", params['port']), SDKHTTPRequestHandler)
        self.__http_server.serve_forever()

    def __extract_params(self) -> dict:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="KubeSpider Source Provider SDK",
            prog='kubespider',
        )
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="The name of the provider"
        )
        parser.add_argument(
            "--port",
            type=int,
            default=9090,
            help="The port to run the provider"
        )
        params = parser.parse_args()
        return vars(params)

    def __call__(self, provider_class):
        provider_api = [func for func in dir(provider_class)
                        if callable(getattr(provider_class, func)) and not func.startswith("__")]
        for api in self.__type.api_list:
            if api not in provider_api:
                raise Exception(
                    f"API <{api}> not found in the <{self.__type.name}> provider")

        if SDKHTTPRequestHandler.PROVIDER:
            raise Exception(
                f'This provider has been bound on <{SDKHTTPRequestHandler.PROVIDER}>')

        SDKHTTPRequestHandler.PROVIDER = provider_class
        # Define the Common API
        setattr(provider_class, "_health", lambda **kwarg: None)
        SDKHTTPRequestHandler.register(provider_class._health, "_health")
        # Register the APIs
        for api in self.__type.api_list:
            SDKHTTPRequestHandler.register(getattr(provider_class, api), api)
        # Start the server
        self.__run()
