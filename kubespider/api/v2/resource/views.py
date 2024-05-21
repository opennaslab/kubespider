import copy
from flask import request
from api.response import success, param_error
from core.plugin.parser import parser_plugin
from core.plugin.search import search_plugin
from utils.values import SearchEvent, Event
from . import resource_blu


@resource_blu.route('/parse', methods=['POST'])
def parse():
    data: dict = request.json
    data_source = data.pop("data_source")
    path = data.pop('path', '')
    if not data_source:
        return param_error(msg="data_source missing")
    parse_event = Event(source=data_source, path=path, force=False, **data)
    parse_result = parser_plugin.parse(event=parse_event)
    return success(data=parse_result)


@resource_blu.route('/search', methods=['POST'])
def search():
    data = copy.deepcopy(request.json)
    keyword = data.pop('keyword', "")
    page = data.pop('page', 1)
    if not keyword:
        return param_error(msg="keyword missing")
    search_event = SearchEvent(keyword=keyword, page=page, **data)
    search_result = search_plugin.search(search_event)
    return success(data=search_result)
