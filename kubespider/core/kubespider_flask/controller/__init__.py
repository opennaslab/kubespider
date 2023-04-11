# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: __init__.py.py
@time: 2023/4/11 19:42
"""
from .kubespider_controller.kubespider_server import kubespider_server as kubespider_server_bp
from .web.rss_list.rss_list import rss_list_bp


def blue_print_register(app):
    app.register_blueprint(kubespider_server_bp)
    app.register_blueprint(rss_list_bp)

