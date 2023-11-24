import asyncio
import logging

from flask import current_app
from transitions.extensions.asyncio import HierarchicalAsyncMachine
from core.exceptions import StateMachineException
from utils.types import States, DownloadStates, FinalStates, StateMachineEvent
from utils.values import Resource
from queue import Queue


class StateMachineTask:
    def __init__(self, resource: Resource, machines):
        self.event_queue = Queue()
        self.model = ResourceModel(resource, self.event_queue)
        self.machines = machines
        self.machine = HierarchicalAsyncMachine(
            model=self.model, states=self.model.STATES, transitions=self.model.TRANSITIONS, initial='initial',
            send_event=True, prepare_event='prepare_event_callback',
            finalize_event='finalize_event_callback',
            on_exception='on_exception',
        )
        self.machines[resource.uuid] = self.model
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_life_cycle())
        self.event_queue.put(StateMachineEvent.start)

    async def start_life_cycle(self):
        event_cycle = []
        while True:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                # trigger event
                await getattr(self.model, event)()
                event_cycle.append(f"<{event}:{self.model.state}>")
            # delete references, release memory
            if self.model.state in [f"{States.final}_{FinalStates.finish}", f"{States.final}_{FinalStates.error}"]:
                # remove state machine and model relationship
                self.machine.remove_model(self.model)
                # remove state machine`s references
                self.machines.pop(self.model.resource.uuid, None)
                # when finish those, state machine`s life cycle is end
                logging.info(f"{self.model.resource} Finished, event:{event_cycle}")
                break
            await asyncio.sleep(1)

    def __del__(self):
        logging.debug("[StateMachineTask] resource:{%s} task has release", str(self.model.resource))


class ResourceModel:
    STATES = [
        {'name': States.initial},
        {'name': States.download, 'children': DownloadStates.download_states},
        {'name': States.archive},
        {'name': States.final, 'children': FinalStates.final_states}
    ]

    TRANSITIONS = [
        dict(trigger=StateMachineEvent.start, source=States.initial, dest=f'{States.download}_{DownloadStates.progress}'
             , after='get_download_event', before='before_download'),

        dict(trigger=StateMachineEvent.stop, source="*", dest=f"{States.final}_{FinalStates.error}", after='exit'),

        dict(trigger=StateMachineEvent.download, source=f"{States.download}_*",
             dest=f'{States.download}_{DownloadStates.progress}', before='before_download'),

        dict(trigger=StateMachineEvent.pause, source=f'{States.download}_{DownloadStates.progress}',
             dest=f'{States.download}_{DownloadStates.paused}', before='before_pause'),

        dict(trigger=StateMachineEvent.cancel, source=f'{States.download}_*',
             dest=f'{States.download}_{DownloadStates.cancel}', before='before_cancel'),

        dict(trigger=StateMachineEvent.fail, source=f'{States.download}_*',
             dest=f'{States.download}_{DownloadStates.fail}', after="after_fail"),

        dict(trigger=StateMachineEvent.complete,
             source=[f'{States.download}_{d}' for d in DownloadStates.download_states],
             dest=f'{States.download}_{DownloadStates.complete}', after="after_complete"),

        dict(trigger=StateMachineEvent.disconnect, source='*', dest=f"{States.final}_{FinalStates.error}",
             after='exit'),

        dict(trigger=StateMachineEvent.finish, source=f"{States.download}_{DownloadStates.complete}",
             dest=f"{States.final}_{FinalStates.finish}", after='exit'),

        dict(trigger=StateMachineEvent.error, source='*', dest=f"{States.final}_{FinalStates.error}", after='exit'),
    ]

    def __init__(self, resource: Resource, event_queue):
        self.resource = resource
        self.event_queue = event_queue
        self.download_provider = self.get_download_provider()
        self.notification_manager = self.get_notification_manager()

    def get_download_provider(self):
        download_manager = current_app.extensions['download_manager']
        return download_manager.get_provider(self.resource)

    @staticmethod
    def get_notification_manager():
        notification_manager = current_app.extensions['notification_manager']
        return notification_manager

    def before_download(self, event):
        if not self.download_provider:
            logging.error("[StateMachine] resource: %s start download, but download provider is None", self.resource)
            self.event_queue.put(StateMachineEvent.error)
        else:
            task = self.download_provider.create_task(self.resource.download_task)
            if task.download_task_id:
                self.notification_manager.send_message(
                    title=f"Task {self.resource} 开始下载",
                    download_provider=self.download_provider.name,
                    download_task_id=task.download_task_id)
            else:
                raise Exception("download failed")

    async def before_pause(self, event):
        download_task = self.download_provider.query_task(self.resource.download_task)
        if download_task.status == DownloadStates.paused:
            success = self.download_provider.paused_task(self.resource.download_task)
            if not success:
                raise StateMachineException(self.state, "Download Pause Failed")

    async def before_cancel(self, event):
        download_task = self.download_provider.query_task(self.resource.download_task)
        if download_task.status == DownloadStates.cancel:
            success = self.download_provider.remove_tasks([self.resource.download_task, ])
            if not success:
                raise StateMachineException(self.state, "Download Cancel Failed")

    def after_complete(self, event):
        self.notification_manager.send_message(
            title=f"Task {self.resource} 任务完成",
            download_provider=self.download_provider.name,
            download_task_id=self.resource.download_task.download_task_id)
        self.event_queue.put(StateMachineEvent.finish)

    def after_fail(self, event):
        self.notification_manager.send_message(
            title=f"Task {self.resource} 任务失败",
            download_provider=self.download_provider.name,
            download_task_id=self.resource.download_task.download_task_id)
        self.event_queue.put(StateMachineEvent.error)

    async def get_download_event(self, event):
        """
        There are two types of changes in the download task state: one is automatic changes over time as the
        download progresses, and the other is changes triggered by user-initiated events. This function's purpose is
        to monitor the state changes resulting from event-triggered changes.
        """

        async def get_download_event():
            try:
                while self.is_download(allow_substates=True):
                    if self.resource.download_task.download_task_id:
                        task = self.download_provider.query_task(self.resource.download_task)
                        if task.status == DownloadStates.paused and self.state != f"{States.download}_{DownloadStates.paused}":
                            # send pause event
                            self.event_queue.put(StateMachineEvent.pause)
                        if task.status == DownloadStates.cancel and self.state != 'download_cancel':
                            # send cancel event
                            self.event_queue.put(StateMachineEvent.cancel)
                        if task.status == DownloadStates.complete and self.state != 'download_complete':
                            # send complete event
                            self.event_queue.put(StateMachineEvent.complete)
                        if task.status == 'fail':
                            # send fail event
                            self.event_queue.put(StateMachineEvent.fail)
                    await asyncio.sleep(5)
            except Exception as err:
                # this asyncio task can not be monitor by state machine so need try catch
                logging.error("[StateMachine] resource: %s ,download event get failed:%s, end the life cycle",
                              self.resource, err)
                self.event_queue.put(StateMachineEvent.error)

        event_loop = asyncio.get_event_loop()
        event_loop.create_task(get_download_event())

    async def prepare_event_callback(self, event):
        state = event.state.name
        event_name = event.event.name
        # todo somethings before event callback

    async def finalize_event_callback(self, event):
        state = event.state.name
        event_name = event.event.name
        # todo somethings after event callback

    def on_exception(self, event):
        try:
            exc = event.error
            event_name = event.event.name
            source_state = getattr(event, 'source_name')
            self.notification_manager.send_message(
                title=f"Task {self.resource}> Failed", error=exc, event_name=event_name,
                source_state=source_state)
            self.event_queue.put(StateMachineEvent.error)
            logging.error(f"[StateMachine] on_exception error handler: {exc}")
        except Exception as e:
            print(f"[StateMachine] An error occurred in on_exception: {e}")
            self.event_queue.put(StateMachineEvent.error)

    async def exit(self, event):
        # todo some thing when exit
        logging.info("[StateMachine] resource: %s end on exit", str(self.resource))

    def __del__(self):
        logging.info("[StateMachine] resource: %s has release", str(self.resource))
