from flask import Blueprint, g, abort

download_blu = Blueprint('download', __name__)
# pylint: disable=cyclic-import
from .views import *


@download_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
