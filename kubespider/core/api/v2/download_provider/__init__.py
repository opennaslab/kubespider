from flask import Blueprint, g, abort

download_provider_blu = Blueprint('download', __name__)
from .views import *


@download_provider_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
