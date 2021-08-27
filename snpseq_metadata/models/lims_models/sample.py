from typing import Dict, Optional, Type, TypeVar

from snpseq_metadata.models.lims_models.metadata_model import LIMSMetadataModel

L = TypeVar("L", bound="LIMSSample")


class LIMSSample(LIMSMetadataModel):
    def __init__(self, sample_id: str, project_id: str, **udf: str):
        self.sample_id = sample_id
        self.project_id = project_id
        for udf_name, udf_value in udf.items():
            setattr(self, udf_name, udf_value)

    def __str__(self) -> str:
        return f"LIMSSample: '{self.sample_id}'"

    def __getattr__(self, name: str) -> object:
        # override the __getattr__ in order to return udf_rml_kitprotocol if
        # udf_library_preparation_kit is missing
        if name == "udf_library_preparation_kit":
            return self.udf_rml_kitprotocol
        raise AttributeError(f"{str(self)} is missing attribute '{name}'")

    def is_paired(self) -> Optional[bool]:
        read_length = getattr(self, "udf_read_length", None)
        if read_length is not None:
            return any([len(read_length.split("+")) > 2, read_length.endswith("x2")])

    @classmethod
    def from_json(cls: Type[L], json_obj: Dict[str, str]) -> L:
        sample_id = json_obj.get("name")
        project_id = json_obj.get("project")
        udf = {k: v for k, v in json_obj.items() if k not in ["name", "project"]}
        return cls(sample_id=sample_id, project_id=project_id, **udf)

    def to_json(self) -> Dict:
        json_obj = {"name": self.sample_id, "project": self.project_id}
        json_obj.update(
            {
                k: v
                for k, v in vars(self).items()
                if k not in ["sample_id", "project_id"]
            }
        )
        return json_obj
