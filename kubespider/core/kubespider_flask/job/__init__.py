# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: __init__.py.py
@time: 2023/4/12 20:32
"""
from .general_period_server import main_rss_period_server
from flask_apscheduler import APScheduler


class Config(object):
    JOBS = [
        {
            'id': 'rss_job',
            'func': __name__ + ':main_rss_period_server',
            'trigger': 'interval',
            'seconds': 3
        }
    ]

    SCHEDULER_API_ENABLED = True


def register_job(app):
    app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()