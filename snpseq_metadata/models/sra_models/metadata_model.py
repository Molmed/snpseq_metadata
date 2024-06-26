import dataclasses
from typing import ClassVar, Dict, Optional, Type, TypeVar, List, Tuple, Iterable

from snpseq_metadata.models.import_export import ModelExporter, ModelImporter
from snpseq_metadata.models.metadata_model import MetadataModel

X = TypeVar("X")
T = TypeVar("T", bound="SRAMetadataModel")


class SRAMetadataModel(MetadataModel):
    model_object_class: ClassVar[Type] = Type[X]
    model_object_meta_class: ClassVar[Optional[Type]] = None
    model_object_parent_field: ClassVar[Optional[Tuple[Type, str]]] = None

    sra_tsv_fields: ClassVar[List[str]] = [
        "study",
        "sample",
        "design_description",
        "library_construction_protocol",
        "library_name",
        "library_strategy",
        "library_source",
        "library_selection",
        "library_layout",
        "insert_size",
        "instrument_model",
        "forward_file_name",
        "forward_file_md5",
        "reverse_file_name",
        "reverse_file_md5",
    ]

    def __init__(self, model_object: model_object_class):
        self.model_object = model_object
        self.model_entity = None
        self.model_meta_name = None
        if self.model_object_parent_field:
            self.model_entity = self.dataclass_entity(
                datacls=self.model_object_parent_field[0],
                cls_field=self.model_object_parent_field[1])
        if self.model_object_meta_class:
            self.model_meta_name = self.model_object_meta_class.Meta.name

        self.exporter = ModelExporter[X]

    def __eq__(self, other: object):
        return super().__eq__(other) and self.to_json() == other.to_json()

    def __getattr__(self, item: str) -> Optional[str]:
        return self.attribute_getter(self, item)

    @staticmethod
    def attribute_getter(obj: T, item: str) -> Optional[str]:
        if item in obj.model_object.__dict__:
            attr = getattr(obj.model_object, item)
            if type(attr) is str:
                return attr

    def to_json(self, **kwargs: Dict) -> Dict:
        return self.exporter.to_json(
            self.model_object,
            self.model_entity,
            self.model_meta_name,
            **kwargs)

    def to_xml(self, **kwargs: Dict) -> str:
        return self.exporter.to_xml(
            self.model_object,
            self.model_entity,
            self.model_meta_name,
            **kwargs)

    def to_manifest(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    def to_tsv(self) -> List[Dict[str, str]]:
        return [{}]

    @classmethod
    def create_object(cls: Type[T], *args, **kwargs) -> T:
        raise NotImplementedError

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        return ModelImporter.from_json(
            json_obj=json_obj, model_cls=cls.model_object_class
        )

    @staticmethod
    def dataclass_entity(datacls: Type, cls_field: str):
        try:
            field = next(
                filter(
                    lambda x: x.name == cls_field,
                    dataclasses.fields(datacls)))
            return field.metadata.get("name")
        except Exception as e:
            return None

    @classmethod
    def from_model_object(cls: Type[T], model_object: model_object_class) -> Optional[T]:
        if type(model_object) == cls.model_object_class:
            return cls(model_object=model_object)
