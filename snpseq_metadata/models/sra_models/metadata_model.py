import dataclasses
from typing import ClassVar, Dict, Optional, Type, TypeVar, List, Tuple

from snpseq_metadata.models.import_export import ModelExporter, ModelImporter
from snpseq_metadata.models.metadata_model import MetadataModel

X = TypeVar("X")
T = TypeVar("T", bound="SRAMetadataModel")


class SRAMetadataModel(MetadataModel):
    model_object_class: ClassVar[Type] = Type[X]
    model_object_meta_class: ClassVar[Optional[Type]] = None
    model_object_parent_field: ClassVar[Optional[Tuple[Type, str]]] = None

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
