from flask import Blueprint

resource_blu = Blueprint('resource', __name__)
from .views import *
