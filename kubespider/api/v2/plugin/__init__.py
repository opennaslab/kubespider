from flask import Blueprint, g, abort

plugin_blu = Blueprint('plugin', __name__)
# pylint: disable=cyclic-import
from .views import *


@plugin_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
