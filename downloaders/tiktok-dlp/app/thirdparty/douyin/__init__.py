#!/usr/bin/env python
# -*- coding: utf-8 -*-

import thirdparty
from thirdparty.common import utils

douyin_headers = {
    'User-Agent': thirdparty.ua,
    'referer': 'https://www.douyin.com/',
    'accept-encoding': None,
    'Cookie': f"msToken={utils.generate_random_str(107)}; ttwid={utils.getttwid()}; odin_tt=324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69; passport_csrf_token=f61602fc63757ae0e4fd9d6bdcee4810;"
}
