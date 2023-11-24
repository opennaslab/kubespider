from flask import Blueprint

source_provider_blu = Blueprint('source', __name__)
from .views import *
