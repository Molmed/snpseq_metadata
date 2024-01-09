from typing import Dict, Optional, Type, TypeVar

from snpseq_metadata.models.lims_models.metadata_model import LIMSMetadataModel

L = TypeVar("L", bound="LIMSSample")


class LIMSSample(LIMSMetadataModel):

    non_udf_fields: Dict[str, str] = {
        "sample_name": "name",
        "sample_id": "sample_id",
        "project_id": "project"
    }

    def __init__(self, sample_name: str, sample_id: str, project_id: str, **udf: str):
        self.sample_name = sample_name
        self.sample_id = sample_id
        self.project_id = project_id
        for udf_name, udf_value in udf.items():
            setattr(self, udf_name, udf_value)

    def __str__(self) -> str:
        return f"LIMSSample: '{self.sample_name}'"

    def __getattr__(self, name: str) -> object:
        # override the __getattr__ in order to return udf_rml_kitprotocol if
        # udf_library_preparation_kit is missing
        if name == "udf_library_preparation_kit":
            return self.udf_rml_kitprotocol
        if name == "udf_insert_size_bp":
            return self.udf_length_current_bp
        if name == "udf_length_current_bp":
            return self.udf_insert_size_bp
        if name == "udf_sample_library_id":
            return self.udf_sample_library_name
        if name == "udf_sample_library_name":
            return f"{self.sample_id}_{self.udf_id}"
        if name in [
            "udf_insert_size_bp",
            "udf_length_current_bp",
            "udf_fragment_size",
            "udf_fragment_lower",
            "udf_fragment_upper"
        ]:
            return None
        raise AttributeError(f"{str(self)} is missing attribute '{name}'")

    def is_paired(self) -> Optional[bool]:
        read_length = getattr(self, "udf_read_length", None)
        if read_length is not None:
            return any([len(read_length.split("+")) > 2, read_length.endswith("x2")])

    def index_tag(self) -> Optional[str]:
        try:
            return "+".join([self.udf_index or None, self.udf_index2 or None])
        except (TypeError, AttributeError) as err:
            try:
                return self.udf_index or ""
            except AttributeError:
                return ""

    @classmethod
    def from_json(cls: Type[L], json_obj: Dict[str, str]) -> L:
        non_udf = {
            k: json_obj.get(v)
            for k, v in cls.non_udf_fields.items()
        }
        udf = {
            k: v
            for k, v in json_obj.items()
            if k not in cls.non_udf_fields.values()
        }
        return cls(
            **non_udf,
            **udf
        )

    def to_json(self) -> Dict:
        json_obj = {
            v: self.__getattribute__(k)
            for k, v in self.non_udf_fields.items()
        }
        json_obj.update(
            {
                k: v
                for k, v in vars(self).items()
                if k not in self.non_udf_fields.keys()
            }
        )
        return json_obj
