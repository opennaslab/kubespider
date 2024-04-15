from flask import Blueprint
from api.response import success

from .binding import binding_blu
from .download import download_blu
from .notification import notification_blu
from .resource import resource_blu
from .plugin import plugin_blu
from .period import period_blu

v2_blu = Blueprint('v2', __name__, url_prefix="/api/v2")

v2_blu.register_blueprint(binding_blu, url_prefix="/binding")
v2_blu.register_blueprint(download_blu, url_prefix="/download")
v2_blu.register_blueprint(notification_blu, url_prefix="/notification")
v2_blu.register_blueprint(plugin_blu, url_prefix="/plugin")
v2_blu.register_blueprint(resource_blu, url_prefix="/resource")
v2_blu.register_blueprint(period_blu, url_prefix="/period")
health_blu = Blueprint('health', __name__, url_prefix="")

v2_blu.register_blueprint(health_blu, url_prefix="/healthz")


@health_blu.route('', methods=['GET'])
def health_check_handler():
    return success()
