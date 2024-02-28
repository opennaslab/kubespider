from flask import Blueprint, g, abort

binding_blu = Blueprint('binding', __name__)
# pylint: disable=cyclic-import
from .views import *


@binding_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
