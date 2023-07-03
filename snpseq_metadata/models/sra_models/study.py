from typing import ClassVar, Optional, Type, TypeVar, List, Tuple

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import Experiment, RefObjectType

T = TypeVar("T", bound="SRAStudyRef")


class SRAStudyRef(SRAMetadataModel):

    model_object_class: ClassVar[Type] = RefObjectType
    model_object_parent_field: ClassVar[Optional[Tuple[Type, str]]] = (Experiment, "study_ref")

    @classmethod
    def create_object(cls: Type[T], refname: str) -> T:
        model_object = cls.model_object_class(refname=refname)
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [("STUDY", self.refname)]

    def __str__(self) -> str:
        return self.refname

    def __hash__(self) -> int:
        return str(self).__hash__()
