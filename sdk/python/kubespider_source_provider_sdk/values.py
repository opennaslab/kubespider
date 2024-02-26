
class ProviderType:

    _registry = {}

    def __init__(self, name: str, api_list: list[str]) -> None:
        self.name = name
        self.api_list = api_list
        ProviderType._registry[name] = self

    @staticmethod
    def get_provider_type(name: str):
        return ProviderType._registry.get(name, None)


ProviderType.parser = ProviderType("parser", ["get_links", "should_handle"])
ProviderType.search = ProviderType("search", ["search"])
