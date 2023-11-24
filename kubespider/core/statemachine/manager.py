import _thread
import asyncio
import gc
import logging

from core.statemachine.machine import StateMachineTask
from flask import Flask
from queue import Queue

from utils.types import StateMachineEvent
from utils.values import Resource


class StateMachineManager:

    def __init__(self, app: Flask = None):
        self.machines = {}
        self.task_queue = Queue(maxsize=100)
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "statemachine_manager" in app.extensions:
            raise RuntimeError(
                "A 'Statemachine' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        app.extensions['statemachine_manager'] = self
        _thread.start_new_thread(self.run, (app,))

    def run(self, app: Flask):
        async def run():
            await asyncio.gather(
                self.consumer_task_queue(app),
            )

        asyncio.run(run())

    async def consumer_task_queue(self, app: Flask):
        with app.app_context():
            while True:
                if not self.task_queue.empty():
                    resource = self.task_queue.get()
                    if resource.uuid not in self.machines.keys():
                        s = StateMachineTask(resource, self.machines)
                        self.machines[resource.uuid] = s
                        logging.info("[StateMachine] task create success, resource: %s", resource)
                await asyncio.sleep(5)
                gc.collect()

    def create_state_machine(self, resource: Resource) -> [None, str]:
        if len(self.machines.keys()) >= 100:
            return "Machine Max Limit"
        elif resource.uuid in self.machines.keys():
            return "This task is exist"
        else:
            self.task_queue.put(resource)

    def trigger_event(self, uuid: str, event: str):
        machine_task = self.machines.get(uuid)
        if not machine_task:
            return "This task is not exist"
        if event not in StateMachineEvent.allow_user_trigger_event:
            return "Event not allowed"
        machine_task.event_queue.put(event)

    def get_state_machines(self):
        data = []
        for machine in self.machines.values():
            data.append({
                'uuid': machine.resource.uuid,
                'name': machine.resource.name,
                'state': machine.state,
            })
        return data
