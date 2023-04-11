# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: __init__.py.py
@time: 2023/4/11 19:42
"""
from flask import Flask
from .controller import blue_print_register


def create_kubespider_app():
    kubespider_app = Flask(__name__, instance_relative_config=True)
    from flask_cors import CORS
    CORS(kubespider_app, supports_credentials=True)
    kubespider_app.config.from_mapping(
        SECRET_KEY="123123"
    )
    blue_print_register(kubespider_app)
    return kubespider_app


if __name__ == '__main__':
    create_kubespider_app()