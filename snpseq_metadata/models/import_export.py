import json
from typing import Dict, Generic, Optional, Tuple, TypeVar, Type

from xsdata.formats.dataclass.serializers.json import JsonSerializer, DictFactory
from xsdata.formats.dataclass.serializers.xml import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.context import XmlContext

from snpseq_metadata.models.custom_json_parser import CustomJsonParser

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
    def serializer_config_context(
            cls: Type[ME],
            obj_entity: Optional[str] = None,
            meta_name: Optional[str] = None,
            xml_declaration: Optional[bool] = True) -> Tuple[SerializerConfig, XmlContext]:
        context = XmlContext(
            element_name_generator=lambda x: obj_entity or meta_name or x.upper())
        config = SerializerConfig(
            pretty_print=True,
            ignore_default_attributes=True,
            xml_declaration=xml_declaration)
        return config, context

    @classmethod
    def to_json(
            cls: Type[ME],
            obj: T,
            obj_entity: Optional[str] = None,
            meta_name: Optional[str] = None,
            xml_declaration: Optional[bool] = True) -> Dict:
        config, context = cls.serializer_config_context(
            obj_entity=obj_entity,
            meta_name=meta_name,
            xml_declaration=xml_declaration)
        serializer = JsonSerializer(
            context=context, indent=2, dict_factory=cls.filter_none_empty, config=config)
        return json.loads(serializer.render(obj))

    @classmethod
    def to_xml(
            cls: Type[ME],
            obj: T,
            obj_entity: Optional[str] = None,
            meta_name: Optional[str] = None,
            xml_declaration: Optional[bool] = True) -> str:
        config, context = cls.serializer_config_context(
            obj_entity=obj_entity,
            meta_name=meta_name,
            xml_declaration=xml_declaration)
        serializer = XmlSerializer(context=context, config=config)
        return serializer.render(obj)


class ModelImporter:

    @staticmethod
    def from_json(json_obj: Dict, model_cls: Type[T]) -> T:
        parser = CustomJsonParser(context=XmlContext())
        return parser.from_string(json.dumps(json_obj), model_cls)
