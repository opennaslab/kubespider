import yaml

from utils.config_reader import YamlFileConfigReader


class ArgumentsFiled:
    name: str
    type: type
    description: str
    required: bool
    default: None
    items: object
    properties: dict

    def __init__(self, **kwargs):
        self._type = self.sting_to_type(kwargs.get("type"))
        if not self._type:
            raise ValueError(f"Invalid argument type, field: {kwargs}")
        self.name = kwargs.get("name", "")
        self.type = kwargs.get("type")
        self.description = kwargs.get("description", "")
        self.required = kwargs.get("required", False)
        self.default = kwargs.get("default", None)
        if self._type == list:
            self.items = self.__class__(**kwargs.get("items", {}))
        if self._type == dict:
            properties = kwargs.get("properties") or {}
            self.properties = {key: self.__class__(**item) for key, item in properties.items()}

    @classmethod
    def type_to_string(cls, _type):
        mapping = {
            str: "text",
            int: "integer",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return mapping.get(_type)

    @classmethod
    def sting_to_type(cls, string: str):
        mapping = {
            "text": str,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return mapping.get((string or "").lower())

    def __repr__(self):
        return self.name or "<UndefinedArgumentsFiled>"

    def serializer(self):
        data = {
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default,
        }
        if items := getattr(self, "items", None):
            data["items"] = items.serializer()
        if properties := getattr(self, "properties", None):
            data["properties"] = {key: property.serializer() for key, property in properties.items()}
        return data

    def validate(self, value):
        # validate required
        if value is None:
            if self.required:
                raise ValueError(f"filed {self.name} is required")
        else:
            # validate filed type
            if not isinstance(value, self._type):
                raise ValueError(f"filed {self.name} type must be {self.type}")
            # validate sub element
            if self.type == "array":
                for arg in value:
                    self.items.validate(arg)
            if self.type == "object":
                for name, filed in self.properties.items():
                    filed.validate(value.get(name, None))


class Definition:
    name: str
    version: str
    author: str
    type: str
    description: str
    language: str
    logo: str
    binary: str
    arguments: dict[str: ArgumentsFiled]

    @classmethod
    def init_from_yaml(cls, yaml_path: str):
        yaml_data = cls.read_yaml(yaml_path)
        return cls.init_from_dict(**yaml_data)

    @classmethod
    def init_from_yaml_bytes(cls, content: bytes):
        yaml_data = yaml.load(content, Loader=yaml.FullLoader)
        return cls.init_from_dict(**yaml_data)

    @classmethod
    def init_from_dict(cls, **kwargs):
        definition = cls()
        definition.name = kwargs.get("name", "")
        definition.version = kwargs.get("version", "")
        definition.author = kwargs.get("author", "")
        definition.type = kwargs.get("type", "")
        definition.description = kwargs.get("description", "")
        definition.language = kwargs.get("language", "")
        definition.logo = kwargs.get("logo", "")
        definition.binary = kwargs.get("binary", "")
        definition.arguments = {
            key: ArgumentsFiled(name=key, **item) for key, item in kwargs.get("arguments", {}).items()
        }
        return definition

    @staticmethod
    def read_yaml(yaml_path):
        return YamlFileConfigReader(yaml_path).read()

    def validate(self, **kwargs):
        arguments = {}
        for key in self.arguments.keys():
            arguments[key] = kwargs.pop(key, None)
        self.validate_arguments(**arguments)

    def validate_arguments(self, **kwargs):
        for name, filed in self.arguments.items():
            filed.validate(kwargs.get(name, None))

    def __repr__(self):
        return self.name or "<UndefinedDefinition>"

    def serializer(self):
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "type": self.type,
            "description": self.description,
            "language": self.language,
            "logo": self.logo,
            "binary": self.binary,
            "arguments": {key: argument.serializer() for key, argument in self.arguments.items()}
        }
