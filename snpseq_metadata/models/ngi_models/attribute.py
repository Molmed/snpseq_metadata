from typing import Dict, Optional, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel

T = TypeVar("T", bound="NGIAttribute")


class NGIAttribute(NGIMetadataModel):
    def __init__(
            self,
            tag: str,
            value: Optional[str] = None,
            units: Optional[str] = None) -> None:
        self.tag = tag
        self.value = value
        self.units = units

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        return cls(
            tag=json_obj.get("tag"),
            value=json_obj.get("value"),
            units=json_obj.get("units"))
