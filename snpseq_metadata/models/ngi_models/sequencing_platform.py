import re
from typing import ClassVar, Dict, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.exceptions import InstrumentModelNotRecognizedException

T = TypeVar("T", bound="NGISequencingPlatform")


class NGISequencingPlatform(NGIMetadataModel):

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

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

    model_name_pattern: ClassVar[str] = r'^(\S+)\s*(X?)'

    def __init__(self, model_name: str) -> None:
        model_name = model_name or ""
        # match name against pattern
        m = re.match(self.model_name_pattern, model_name)
        model_name = model_name if not m else "".join(m.groups())
        if model_name.lower() not in map(str.lower, self.model_dict.values()):
            raise InstrumentModelNotRecognizedException(needle=model_name)
        super().__init__(model_name)

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
