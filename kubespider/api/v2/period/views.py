from flask import request
from api.response import success
from api.v2.period import period_blu
from core.period_manager import period_manager


@period_blu.route('', methods=['GET'])
def get_period_task():
    tasks = period_manager.get_tasks()
    return success(tasks)


@period_blu.route('', methods=['POST'])
def create_or_update_period_task():
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


@period_blu.route('/<int:task_id>', methods=['DELETE'])
def delete_period_task(task_id: int):
    period_manager.delete_task(task_id)
    return success()


@period_blu.route('/operate', methods=['PUT'])
def operate_period_task():
    body: dict = request.json
    task_id: int = body.get("id")
    enable: bool = body.get("enable", False)
    if enable:
        period_manager.enable(task_id)
    else:
        period_manager.disable(task_id)
    return success()
