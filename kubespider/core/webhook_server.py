import logging
import json

from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS

from api.values import Event
from utils import global_config
from core import notification_server
from core import period_server
from core.kubespider_controller import kubespider_controller
from core import source_manager

kubespider_server = Flask(__name__)
CORS(kubespider_server)

def auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not check_auth(request.headers):
            return not_authenticated()
        return func(*args, **kwargs)

    return decorated


@kubespider_server.route('/healthz', methods=['GET'])
def health_check_handler():
    resp = jsonify('OK')
    resp.status_code = 200
    return resp


@kubespider_server.route('/api/v1/downloadproviders', methods=['GET'])
@auth_required
def list_download_provider_handler():
    download_providers = kubespider_controller.download_providers

    resp_array = {}
    for i in download_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@kubespider_server.route('/api/v1/sourceproviders', methods=['GET'])
@auth_required
def list_source_provider_handler():
    source_providers = kubespider_controller.source_providers

    resp_array = {}
    for i in source_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@kubespider_server.route('/api/v1/ptproviders', methods=['GET'])
@auth_required
def list_pt_provider_handler():
    pt_providers = kubespider_controller.pt_providers

    resp_array = {}
    for i in pt_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@kubespider_server.route('/api/v1/download', methods=['POST'])
@auth_required
def download_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    source = data.pop('dataSource')
    path = data.pop('path', '')
    logging.info('Get webhook trigger:%s', source)
    event = Event(source, path, **data)

    err = source_manager.source_provider_manager.download_with_source_provider(event)

    if err is None:
        notification_server.kubespider_notification_server.send_message(
            title="[webhook] start download", source=source, path=path
        )
        return send_ok_response()
    notification_server.kubespider_notification_server.send_message(
        title="[webhook] download failed", source=source, path=path
    )
    return send_bad_response(err)


@kubespider_server.route('/api/v1/refresh', methods=['GET'])
@auth_required
def refresh_handler():
    period_server.kubespider_period_server.trigger_run()
    return send_ok_response()


def send_ok_response():
    resp = jsonify('OK')
    resp.status_code = 200
    resp.content_type = 'application/text'
    return resp


def send_bad_response(err):
    resp = jsonify(str(err))
    resp.status_code = 500
    resp.content_type = 'application/text'
    return resp


def check_auth(headers):
    auth_token = global_config.get_auth_token()
    if auth_token is None:
        return True
    if headers is None:
        return False
    authorization = headers.get("Authorization")
    if not authorization:
        return False
    try:
        auth_type, auth_info = authorization.split(None, 1)
        auth_type = auth_type.lower()
    except ValueError:
        return False
    if auth_type == "bearer" and auth_info == auth_token:
        return True
    return False


def not_authenticated():
    resp = jsonify('Auth Required')
    resp.status_code = 401
    resp.content_type = 'application/text'
    return resp
