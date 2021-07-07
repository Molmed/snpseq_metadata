import json
from typing import Dict, Generic, Tuple, TypeVar, Type

from xsdata.formats.dataclass.serializers.json import JsonSerializer, DictFactory
from xsdata.formats.dataclass.serializers.xml import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.context import XmlContext

from xsdata.formats.dataclass.parsers import JsonParser

T = TypeVar("T")
ME = TypeVar("ME", bound="ModelExporter")


class ModelExporter(Generic[T]):
    @staticmethod
    def filter_none_empty(x: Tuple) -> Dict:
        return {
            k: v
            for k, v in DictFactory.FILTER_NONE(x).items()
            if v is not None and (type(v) is not list or len(v) > 0)
        }

    @classmethod
    def to_json(cls: Type[ME], obj: T) -> Dict:
        serializer = JsonSerializer(
            context=XmlContext(), indent=2, dict_factory=cls.filter_none_empty
        )
        return json.loads(serializer.render(obj))

    @classmethod
    def to_xml(cls: Type[ME], obj: T) -> str:
        context = XmlContext(element_name_generator=str.upper)
        config = SerializerConfig(pretty_print=True)
        serializer = XmlSerializer(context=context, config=config)
        return serializer.render(obj)


class ModelImporter:
    @staticmethod
    def from_json(json_obj: Dict, model_cls: Type[T]) -> T:
        parser = JsonParser(context=XmlContext())
        return parser.from_string(json.dumps(json_obj), model_cls)
