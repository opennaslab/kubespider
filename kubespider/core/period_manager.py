import copy
from flask_apscheduler import APScheduler
from apscheduler.jobstores.base import JobLookupError

from core.plugin.binding import plugin_binding
from core.plugin.search import search_plugin
from core.plugin.scheduler import scheduler_plugin
from models import get_session
from models.models import PeriodTask, Binding, Resource, Plugin
from utils.values import SearchEvent


class PeriodManager:

    def __init__(self) -> None:
        self.session = get_session()
        self.scheduler = APScheduler()
        self.scheduler.start()

    @staticmethod
    def get_tasks():
        tasks = []
        for task in PeriodTask.query.all():
            item = tasks.serializer()
            binding_id_list = task.bindings.split(",")
            item["bindings"] = [{"id": binding.id, "name": binding.name} for binding in
                                Binding.query.filter(id__in=binding_id_list).all()]
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
            task.binding_ids = ",".join([binding.get("id") for binding in bindings])
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
            task.binding_ids = ",".join([binding.get("id") for binding in bindings])
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

    def enable(self, task_id: int):
        task = self.session.query(PeriodTask).filter_by(id=task_id).first()
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

    def __add_task(self, task: PeriodTask):
        if task.task_type == "search":
            kwargs = copy.deepcopy(task.arguments)
            kwargs['binding_ids'] = task.binding_ids
            self.scheduler.add_job(id=task.name, func=self.period_search_task, trigger='interval', seconds=10,
                                   kwargs=kwargs)
        elif task.task_type == "scheduler":
            kwargs = copy.deepcopy(task.arguments)
            kwargs['binding_ids'] = task.binding_ids
            self.scheduler.add_job(id=task.name, func=self.period_scheduler_task, trigger='interval',
                                   seconds=10, kwargs=kwargs)

    def __remove_task(self, task_name: str):
        try:
            self.scheduler.remove_job(id=task_name)
        except JobLookupError:
            ...

    @staticmethod
    def period_search_task(**kwargs):
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
                    model = Resource(**resource)
                    model.plugin_id = plugin.id if plugin else None
                    resource_models.append(model)
            session.bulk_save_objects(resource_models)

    @staticmethod
    def period_scheduler_task(**kwargs):
        binding_ids = kwargs.get("binding_ids", "").split(",")
        bindings = plugin_binding.list_config(ids=binding_ids)
        scheduler_providers = scheduler_plugin.wrap_scheduler_provider(bindings)
        scheduler_result = scheduler_plugin.scheduler(scheduler_providers)
        session = get_session()
        resource_models = []
        for item in scheduler_result:
            resources = item.get("data")
            plugin = session.query(Plugin).filter_by(name=item.get("plugin")).first()
            for resource in resources:
                model = Resource(**resource)
                model.plugin_id = plugin.id if plugin else None
                resource_models.append(model)
        session.bulk_save_objects(resource_models)
