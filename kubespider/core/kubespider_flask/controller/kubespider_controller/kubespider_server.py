# -*- coding: utf-8 -*-

"""
@author: jwcesign, ijwstl
@software: PyCharm
@file: kubespider_server.py
@time: 2023/4/11 19:45
"""
import os
import sys
import json
import logging
import flask
from flask import Blueprint, jsonify, request
from urllib.parse import urlparse

from core import download_trigger
from core import kubespider_global
from core import period_server
from source_provider import provider as sp
from api import types
from utils import helper

kubespider_server = flask.Blueprint("kubespider_server", __name__, url_prefix="/")


@kubespider_server.route('/healthz', methods = ['GET'])
def health_check_handler():
    resp = jsonify('OK')
    resp.status_code = 200
    return resp

@kubespider_server.route('/api/v1/downloadproviders', methods = ['GET'])
def list_download_provider_handler():
    resp_array = {}
    for i in kubespider_global.download_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp

@kubespider_server.route('/api/v1/sourceproviders', methods = ['GET'])
def list_source_provider_handler():
    resp_array = {}
    for i in kubespider_global.source_providers:
        resp_array[i.get_provider_name()] = i.provider_enabled()
    resp = jsonify(resp_array)
    resp.content_type = "application/json"
    return resp

@kubespider_server.route('/api/v1/download', methods = ['POST'])
def download_handler():
    data = json.loads(request.data.decode("utf-8"))
    source = data['dataSource']
    path = ''
    if 'path' in data.keys():
        path = data['path']
    logging.info('Get webhook trigger:%s', source)

    match_one_provider = False
    match_provider = None
    for provider in kubespider_global.enabled_source_provider:
        if provider.is_webhook_enable() and provider.should_handle(source):
            match_provider = provider
            # Do not break here, in order to check whether it matchs multiple provider
            match_one_provider = True

    err = None
    if match_one_provider is False:
        link_type = get_link_type(source)
        # If we not match the source provider, just download to common path
        # TODO: implement a better classification if no source provider match
        path = helper.convert_file_type_to_path(types.FILE_TYPE_COMMON) + '/' + path
        err = download_trigger.kubespider_downloader.download_file(source, path, link_type)

    if match_one_provider is True:
        if match_provider.get_provider_type() == types.SOURCE_PROVIDER_DISPOSABLE_TYPE:
            err = download_links_with_provider(source, match_provider)
        else:
            match_provider.update_config(source)
            period_server.kubespider_period_server.trigger_run()

    if err is None:
        return send_ok_response()
    return send_bad_response(err)

@kubespider_server.route('/api/v1/refresh', methods = ['GET'])
def refresh_handler():
    period_server.kubespider_period_server.trigger_run()
    return send_ok_response()

def download_links_with_provider(source: str, source_provider: sp.SourceProvider):
    link_type = source_provider.get_link_type()
    links = source_provider.get_links(source)
    specific_download_provider = source_provider.get_download_provider()
    for download_link in links:
        # The path rule should be like: {file_type}/{file_title}
        download_final_path = helper.convert_file_type_to_path(download_link['file_type']) + '/' + download_link['path']
        err = download_trigger.kubespider_downloader.\
            download_file(download_link['link'], \
                          download_final_path, link_type,\
                            specific_download_provider)
        if err is not None:
            return err
    return None

def get_link_type(url):
    if url.startswith('magnet:'):
        return types.LINK_TYPE_MAGNET
    if urlparse(url).path.endswith('torrent'):
        return types.LINK_TYPE_TORRENT

    # TODO: implement other type, like music mv or short video
    return types.LINK_TYPE_GENERAL

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

if __name__ == '__main__':
    print(123)