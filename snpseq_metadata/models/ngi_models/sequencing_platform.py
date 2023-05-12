import re
from typing import ClassVar, Dict, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.exceptions import InstrumentModelNotRecognizedException

T = TypeVar("T", bound="NGISequencingPlatform")


class NGISequencingPlatform(NGIMetadataModel):
    def __init__(self, model_name: str) -> None:
        # split on whitespace
        self.model_name = model_name.split()[0]

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        return cls(model_name=json_obj.get("model_name"))


class NGIIlluminaSequencingPlatform(NGISequencingPlatform):

    model_dict: ClassVar[Dict[str, str]] = {
        "lh": "NovaSeqX",
        "a": "NovaSeq",
        "m": "MiSeq",
        "fs": "iSeq",
        "st-e": "HiSeqX",
        "d": "HiSeq2500",
        "sn": "HiSeq",
    }

    @classmethod
    def model_name_from_id(cls: Type[T], model_id: str) -> str:
        try:
            m = re.match(r"^(\D+)\d+", model_id)
            model_prefix = m.group(1)
        except AttributeError:
            model_prefix = model_id

        return cls._object_from_something(
            needle=model_prefix,
            haystack=cls.model_dict,
            on_error=InstrumentModelNotRecognizedException,
        )
