from typing import Dict, Type, TypeVar

from snpseq_metadata.models.lims_models.metadata_model import LIMSMetadataModel

L = TypeVar("L", bound="LIMSSample")


class LIMSSample(LIMSMetadataModel):
    def __init__(self, sample_id: str, project_id: str, **udf: str):
        self.sample_id = sample_id
        self.project_id = project_id
        for udf_name, udf_value in udf.items():
            setattr(self, udf_name, udf_value)

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
