from typing import Dict, List, Optional, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.models.ngi_models.sample import NGISampleDescriptor

T = TypeVar("T", bound="NGIPool")
M = TypeVar("M", bound="NGIPoolMember")
L = TypeVar("L", bound="NGIReadLabel")


class NGIReadLabel(NGIMetadataModel):

    def __init__(
            self,
            label: str,
            read_group_tag: Optional[str] = None
    ) -> None:
        self.label = label
        self.read_group_tag = read_group_tag

    @classmethod
    def from_json(cls: Type[L], json_obj: Dict) -> L:
        return cls(
            label=json_obj["label"],
            read_group_tag=json_obj.get("read_group_tag")
        )


class NGIPoolMember(NGISampleDescriptor):

    def member_name(self) -> str:
        return self.sample_name or self.sample_id

    def read_labels(self) -> Optional[List[NGIReadLabel]]:
        return [
            NGIReadLabel(
                label=tag,
                read_group_tag=self.sample_library_id or self.sample_id
            )
            for tag in self.library_tags()
        ] or None


class NGIPool(NGIMetadataModel):

    def __init__(
            self,
            samples: List[NGIPoolMember]
    ) -> None:
        self.samples = samples

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        if json_obj:
            members = [
                NGIPoolMember.from_json(json_obj=sample_json)
                for sample_json in json_obj.get("samples", [])
            ]
            return NGIPool(
                samples=members
            )
