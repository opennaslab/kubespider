import logging
import json

from flask import jsonify, request
from core import notification_manager, period_server
from core import download_manager
from core.plugin.parser import parser_plugin
from core.download_manager import download_manager
from core.kubespider_controller import kubespider_controller
from utils.values import Event
from api.v1 import v1_blu


@v1_blu.route('/downloadproviders', methods=['GET'])
def list_download_provider_handler():
    download_providers = download_manager.instances

    resp_array = {}
    for i in download_providers:
        resp_array[i.name] = i.is_active
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@v1_blu.route('/sourceproviders', methods=['GET'])
def list_source_provider_handler():
    source_providers = kubespider_controller.source_providers

    resp_array = {}
    for i in source_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@v1_blu.route('/ptproviders', methods=['GET'])
def list_pt_provider_handler():
    pt_providers = kubespider_controller.pt_providers

    resp_array = {}
    for i in pt_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp


@v1_blu.route('/download', methods=['POST'])
def download_handler():
    data: dict = json.loads(request.data.decode("utf-8"))
    source = data.pop('dataSource')
    path = data.pop('path', '')
    logging.info('Get webhook trigger:%s', source)
    event = Event(source, path, **data)

    err = parser_plugin.download_with_parser_provider(event)

    if err is None:
        notification_manager.send_message(
            title="[webhook] start download", source=source, path=path
        )
        return send_ok_response()
    notification_manager.send_message(
        title="[webhook] download failed", source=source, path=path
    )
    return send_bad_response(err)


@v1_blu.route('/refresh', methods=['GET'])
def refresh_handler():
    period_server.kubespider_period_server.trigger_run()
    return send_ok_response()


def send_ok_response():
    resp = jsonify('OK')
    resp.status_code = 200
    resp.content_type = 'application/text'
    return resp


def send_json_response(data):
    resp = jsonify(data)
    resp.status_code = 200
    resp.content_type = 'application/json'
    return resp


def send_bad_response(err):
    resp = jsonify(str(err))
    resp.status_code = 500
    resp.content_type = 'application/text'
    return resp
