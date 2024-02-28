from flask import Blueprint, g, abort

v1_blu = Blueprint('v1', __name__, url_prefix="/api/v1")
# pylint: disable=cyclic-import
from .views import *


@v1_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')


health_blu = Blueprint('health', __name__, url_prefix="")


@health_blu.route('/healthz', methods=['GET'])
def health_check_handler():
    resp = jsonify('OK')
    resp.status_code = 200
    return resp
