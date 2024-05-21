from flask import Blueprint, g, abort

period_blu = Blueprint('period', __name__)
# pylint: disable=cyclic-import
from .views import *


@period_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
