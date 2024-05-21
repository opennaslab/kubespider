import abc

from utils.values import Resource


class SchedulerProvider(metaclass=abc.ABCMeta):

    def __init__(self, plugin_bind, plugin_instance):
        self.bind = plugin_bind
        self.plugin_instance = plugin_instance

    def get_provider_name(self) -> str:
        # name of source provider defined in config
        return self.bind.name

    def get_download_param(self) -> dict:
        # get the specific params for downloader
        return self.bind.arguments

    def get_download_provider_type(self):
        pass

    def get_prefer_download_provider(self):
        pass

    @abc.abstractmethod
    def get_cost_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def get_max_sum_size(self) -> float:
        pass

    def scheduler(self) -> list[Resource]:
        # Return the download resources from the scheduler provider
        resources = []
        for item in self.plugin_instance.call_api("scheduler", **self.bind.arguments):
            resources.append(Resource(**item))
        return resources
