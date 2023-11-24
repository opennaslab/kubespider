from flask import request, current_app

from core.api.response import success
from core.api.v2.statemachine import statemachine_blu


@statemachine_blu.route("/", methods=["GET"])
def get_statemachine_view():
    # todo
    statemachine_manager = current_app.extensions['statemachine_manager']
    result = statemachine_manager.get_state_machines()
    return success(data=result)


@statemachine_blu.route("/create_task", methods=["POST"])
def create_task():
    # todo
    statemachine_manager = current_app.extensions['statemachine_manager']
    resource = request.json
    result = statemachine_manager.create_state_machine_task(resource)
    return result


@statemachine_blu.route("/remove_task", methods=["POST"])
def remove_task():
    # todo
    statemachine_manager = current_app.extensions['statemachine_manager']
    resource = request.json
    result = statemachine_manager.create_state_machine_task(resource)
    return result


@statemachine_blu.route("/tigger_event", methods=["POST"])
def tigger_event():
    # todo
    statemachine_manager = current_app.extensions['statemachine_manager']
    event = request.json
    result = statemachine_manager.tigger_event(event)
    return result
