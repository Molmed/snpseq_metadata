from typing import Dict, List, Optional, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel

T = TypeVar("T", bound="NGISampleDescriptor")


class NGISampleDescriptor(NGIMetadataModel):
    def __init__(
            self,
            sample_name: str,
            sample_id: Optional[str] = None,
            sample_library_id: Optional[str] = None,
            sample_library_tag: Optional[str] = None) -> None:
        self.sample_name = sample_name
        self.sample_id = sample_id
        self.sample_library_id = sample_library_id
        self.sample_library_tag = sample_library_tag

    def sample_alias(self):
        return self.sample_library_id

    def library_tags(self) -> List[str]:
        return self.sample_library_tag.split("+")

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        if json_obj:
            return cls(
                sample_name=json_obj.get("sample_name"),
                sample_id=json_obj.get("sample_id"),
                sample_library_id=json_obj.get("sample_library_id"),
                sample_library_tag=json_obj.get("sample_library_tag"))
