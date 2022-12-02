import abc

class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def should_handle(self, dataSourceUrl):
        pass

    @abc.abstractmethod
    def get_provider_type(self):
        pass
    
    @abc.abstractmethod
    def get_provider_name(self):
        pass
    
    @abc.abstractmethod
    def load_config(self, cfg):
        pass