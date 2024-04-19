import copy
import logging
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from core.plugin.binding import plugin_binding
from core.plugin.search import search_plugin
from models import get_session
from models.models import PeriodTask, Binding, Resource, Plugin
from utils.values import SearchEvent


class PeriodManager:

    def __init__(self) -> None:
        self.session = get_session()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def get_tasks(self):
        tasks = []
        for task in self.session.query(PeriodTask).all():
            item = task.serializer()
            binding_id_list = task.binding_ids.split(",")
            item["bindings"] = [
                {"id": binding.id, "name": binding.name} for binding in
                self.session.query(Binding).filter(Binding.id.in_(binding_id_list)).all()
            ]
            tasks.append(item)
        return tasks

    def create_or_update_task(
            self, name: str, task_type: str, tigger_type: str, tigger_config: dict, arguments: dict, bindings: list,
            task_id: int = None):
        if task_id:
            task = self.session.query(PeriodTask).filter_by(id=task_id).first()
            if not task:
                raise ValueError("Task does not exist.")
            old_name = task.name
            task.name = name
            task.task_type = task_type
            task.tigger_type = tigger_type
            task.tigger_config = tigger_config
            task.arguments = arguments
            task.binding_ids = ",".join([str(binding) for binding in bindings])
            task.enable = False
            self.session.add(task)
            self.session.commit()
            self.__remove_task(old_name)
        else:
            task = PeriodTask()
            task.name = name
            task.task_type = task_type
            task.tigger_type = tigger_type
            task.tigger_config = tigger_config
            task.arguments = arguments
            task.binding_ids = ",".join([str(binding) for binding in bindings])
            task.enable = False
            self.session.add(task)
            self.session.commit()

    def delete_task(self, task: [int, PeriodTask]):
        task = self.session.query(PeriodTask).filter_by(id=task).first() if isinstance(task, int) else task
        if not isinstance(task, PeriodTask):
            raise ValueError("Task not found")
        self.__remove_task(task.name)
        self.session.delete(task)
        self.session.commit()

    def enable(self, task: [int, PeriodTask]):
        task = self.session.query(PeriodTask).filter_by(id=task).first() if isinstance(task, int) else task
        self.__add_task(task)
        task.enable = True
        self.session.add(task)
        self.session.commit()

    def disable(self, task_id: int):
        task = self.session.query(PeriodTask).filter_by(id=task_id).first()
        self.__remove_task(task)
        task.enable = False
        self.session.add(task)
        self.session.commit()

    @staticmethod
    def __get_tigger(task: PeriodTask):
        if task.tigger_type == 'interval':
            trigger = IntervalTrigger(**task.tigger_config)
        elif task.tigger_type == 'date':
            trigger = DateTrigger(**task.tigger_config)
        elif task.tigger_type == 'cron':
            trigger = CronTrigger(**task.tigger_config)
        else:
            raise ValueError("Invalid trigger type")
        return trigger

    def __add_task(self, task: PeriodTask):
        tigger = self.__get_tigger(task)
        if task.task_type == "search":
            kwargs = copy.deepcopy(task.arguments)
            kwargs['binding_ids'] = task.binding_ids
            self.scheduler.add_job(id=task.name, func=self.period_search_task, trigger=tigger, kwargs=kwargs)
        elif task.task_type == "scheduler":
            kwargs = copy.deepcopy(task.arguments)
            kwargs['binding_ids'] = task.binding_ids
            self.scheduler.add_job(id=task.name, func=self.period_scheduler_task, trigger='tigger', kwargs=kwargs)

    def __remove_task(self, task_name: str):
        try:
            self.scheduler.remove_job(job_id=task_name)
        except JobLookupError:
            ...

    @staticmethod
    def period_search_task(**kwargs):
        try:
            keyword = kwargs.get("keyword")
            binding_ids = kwargs.get("binding_ids", "").split(",")
            if keyword:
                bindings = plugin_binding.list_config(ids=binding_ids)
                search_providers = search_plugin.wrap_search_provider(bindings)
                search_event = SearchEvent(keyword=keyword, page=1)
                search_result = search_plugin.search(search_event, search_providers)
                session = get_session()
                resource_models = []
                for item in search_result:
                    resources = item.get("data")
                    plugin = session.query(Plugin).filter_by(name=item.get("plugin")).first()
                    for resource in resources:
                        model = session.query(Resource).filter_by(uid=resource.get("uid")).first()
                        if not model:
                            model = Resource()
                            model.name = resource.get("name")
                            model.uid = resource.get("uid")
                            model.url = resource.get("url")
                            model.path = resource.get("path")
                            model.link_type = resource.get("link_type")
                            model.file_type = resource.get("file_type")
                            model.title = resource.get("title")
                            model.subtitle = resource.get("subtitle")
                            model.desc = resource.get("desc")
                            model.poster = resource.get("poster")
                            model.size = resource.get("size")
                            model.publish_time = resource.get("publish_time")
                            model.discover_time = resource.get("discover_time")
                            model.plugin_id = plugin.id if plugin else None
                            resource_models.append(model)
                session.bulk_save_objects(resource_models)
                session.commit()
                logging.info("[PeriodManager] search task finished, find %s resources" % len(resource_models))
        except Exception as e:
            logging.error("[PeriodManager] search task failed with exception:\n %s", traceback.format_exc())

    @staticmethod
    def period_scheduler_task(**kwargs):
        # TODO
        pass

    def period_run(self):
        for task in self.session.query(PeriodTask).all():
            if task.enable:
                self.enable(task)


period_manager = PeriodManager()
