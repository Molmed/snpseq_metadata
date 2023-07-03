from typing import ClassVar, Optional, Type, TypeVar, List, Tuple

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import AttributeType

T = TypeVar("T", bound="SRAAttribute")


class SRAAttribute(SRAMetadataModel):

    model_object_class: ClassVar[Type] = AttributeType

    @classmethod
    def create_object(
            cls: Type[T],
            tag: str,
            value: Optional[str] = None,
            units: Optional[str] = None) -> T:
        model_object = cls.model_object_class(tag=tag, value=value, units=units)
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [(
            self.tag.upper(),
            f"{self.value} {self.units or ''}")]

    def __str__(self) -> str:
        return f"{self.tag} = " \
               f"{self.value} " \
               f"{self.units or ''}"

    def __hash__(self) -> int:
        return str(self).__hash__()
