from flask import Blueprint, abort, g

resource_blu = Blueprint('resource', __name__)
# pylint: disable=cyclic-import
from .views import *


@resource_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
