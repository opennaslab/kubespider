from flask import Blueprint

system_blu = Blueprint('system', __name__)
from .views import *
