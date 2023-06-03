import json
import os

from flask import Flask,jsonify,request

from core import tasks

you_get_server = Flask(__name__)

@you_get_server.route('/api/v1/download', methods = ['POST'])
def download_handler():
    data = json.loads(request.data.decode("utf-8"))
    source = data['dataSource']
    path = os.path.join('/app/downloads', data['path'])
    args = [source, '-o', path]

    tasks.you_get_tasks.equeue(tasks.DownloadTask(args, 0))
    return send_ok_response()

def send_ok_response():
    resp = jsonify('OK')
    resp.status_code = 200
    resp.content_type = 'application/text'
    return resp
