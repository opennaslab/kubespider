from models import get_session
from models.models import Plugin, Binding


class PluginBinding:

    def __init__(self) -> None:
        self.session = get_session()

    def list_config(self, config_type: str = None, ids: list = None) -> list[Binding]:
        query = self.session.query(Binding)
        if config_type:
            query = query.filter_by(type=config_type)
        if ids:
            query = query.filter_by(Binding.id.in_(ids))
        return query.all()

    def create_or_update(self, **config_data: dict) -> None:
        _id = config_data.pop('id', None)
        name = config_data.pop('name', "")
        config_type = config_data.pop('type')
        plugin_name = config_data.pop('plugin_name')
        plugin = self.session.query(Plugin).filter_by(name=plugin_name).first()
        if not all([name, config_type, plugin_name]):
            raise Exception('name and plugin_name are required')
        bind_model = self.session.query(Binding).filter_by(id=_id).first() or Binding()
        bind_model.name = name
        bind_model.type = config_type
        bind_model.plugin_id = plugin.id
        bind_model.arguments = config_data
        bind_model.plugin_instance = plugin
        self.__validate(bind_model)
        self.session.add(bind_model)
        self.session.commit()

    def remove(self, _id: int) -> None:
        config_model = self.session.query(Binding).filter_by(id=_id).first()
        if config_model:
            self.session.delete(config_model)
            self.session.commit()

    @staticmethod
    def __validate(config: Binding):
        from core.plugin.manager import plugin_manager
        plugin_definition = plugin_manager.get_plugin(config.plugin.name)
        if not plugin_definition:
            raise Exception('plugin not found')
        plugin_definition.validate(**config.arguments)


plugin_binding: PluginBinding = PluginBinding()
