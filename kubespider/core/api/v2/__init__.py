from flask import Blueprint

from .download_provider import download_provider_blu
from .notification_provider import notification_provider_blu
from .resource import resource_blu
from .source_provider import source_provider_blu
from .statemachine import statemachine_blu
from .system import system_blu

v2_blu = Blueprint('v2', __name__, url_prefix="/api/v2")

v2_blu.register_blueprint(download_provider_blu, url_prefix="/provider/download")
v2_blu.register_blueprint(notification_provider_blu, url_prefix="/provider/notification")
v2_blu.register_blueprint(source_provider_blu, url_prefix="/provider/source")
v2_blu.register_blueprint(resource_blu, url_prefix="/resource")
v2_blu.register_blueprint(statemachine_blu, url_prefix="/statemachine")
v2_blu.register_blueprint(system_blu, url_prefix="/system")
