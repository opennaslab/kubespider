from flask import Blueprint

statemachine_blu = Blueprint('statemachine', __name__)
from .views import *
