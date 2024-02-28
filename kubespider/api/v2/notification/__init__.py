from flask import Blueprint, g, abort

notification_blu = Blueprint('notification', __name__)
from .views import *


@notification_blu.before_request
def auth_require():
    if not g.auth:
        abort(401, 'Unauthorized')
