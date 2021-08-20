from typing import ClassVar, Dict, Type, TypeVar, List, Tuple

from snpseq_metadata.models.import_export import ModelExporter, ModelImporter
from snpseq_metadata.models.metadata_model import MetadataModel

X = TypeVar("X")
T = TypeVar("T", bound="SRAMetadataModel")


class SRAMetadataModel(MetadataModel):
    model_object_class: ClassVar[Type] = Type[X]

    def __init__(self, model_object: model_object_class):
        self.model_object = model_object
        self.exporter = ModelExporter[X]

    def __eq__(self, other: object):
        return super().__eq__(other) and self.to_json() == other.to_json()

    def to_json(self) -> Dict:
        return self.exporter.to_json(self.model_object)

    def to_xml(self) -> str:
        return self.exporter.to_xml(self.model_object)

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
