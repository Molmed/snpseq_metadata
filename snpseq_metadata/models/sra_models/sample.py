from typing import ClassVar, Type, TypeVar, Tuple, List

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import SampleDescriptorType

T = TypeVar("T", bound="SRASampleDescriptor")


class SRASampleDescriptor(SRAMetadataModel):

    model_object_class: ClassVar[Type] = SampleDescriptorType

    @classmethod
    def create_object(cls: Type[T], refname: str) -> T:
        model_object = SampleDescriptorType(refname=refname)
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [("SAMPLE", self.model_object.refname)]

    def __str__(self) -> str:
        return self.model_object.refname
