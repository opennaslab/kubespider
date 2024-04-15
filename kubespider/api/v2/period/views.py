import json
from flask import request, current_app
from api.response import success, param_error
from api.v2.period import period_blu


@period_blu.route('', methods=['GET'])
def get_period_task():
    period_manager = current_app.extensions["period_manager"]
    tasks = period_manager.get_tasks()
    return success(tasks)


@period_blu.route('', methods=['POST'])
def modify_period_task():
    period_manager = current_app.extensions["period_manager"]
    body: dict = request.json
    name: str = body.get("name")
    task_type: str = body.get("task_type")
    tigger_type: str = body.get("tigger_type")
    tigger_config: dict = body.get("tigger_config")
    arguments: dict = body.get("arguments")
    bindings: list = body.get("bindings")
    task_id: int = body.get("id")
    period_manager.create_or_update_task(name, task_type, tigger_type, tigger_config, arguments, bindings, task_id)
    return success()


@period_blu.route('/<task_id>', methods=['DELETE'])
def delete_period_task(task_id):
    period_manager = current_app.extensions["period_manager"]
    period_manager.delete_task(task_id)
    return success()
