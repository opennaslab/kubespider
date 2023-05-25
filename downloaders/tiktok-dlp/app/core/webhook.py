import json
import os

from flask import Flask, jsonify, request
from core import tasks

tiktok_dlp = Flask(__name__)


@tiktok_dlp.route('/api/v1/download', methods=['POST'])
def download_handler():
    para = json.loads(request.data.decode("utf-8"))
    para['path'] = os.path.join('/root/downloads', para['path'])
    tasks.tiktok_dlp_tasks.equeue(tasks.DownloadTask(para, 0))
    return send_ok_response()


def send_ok_response():
    resp = jsonify('OK')
    resp.status_code = 200
    resp.content_type = 'application/text'
    return resp
