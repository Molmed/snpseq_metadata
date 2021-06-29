from typing import ClassVar, List, Dict, Optional, Type, TypeVar
import datetime

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.models.ngi_models.experiment import NGIExperimentBase
from snpseq_metadata.models.ngi_models.file_models import NGIFastqFile
from snpseq_metadata.models.ngi_models.sequencing_platform import (
    NGIIlluminaSequencingPlatform,
)

T = TypeVar("T", bound="NGIRun")


class NGIRun(NGIMetadataModel):

    run_center: ClassVar[str] = "National Genomics Infrastructure, Uppsala"

    def __init__(
        self,
        run_alias: str,
        experiment: NGIExperimentBase,
        platform: NGIIlluminaSequencingPlatform,
        run_date: Optional[datetime.datetime] = None,
        fastqfiles: Optional[List[NGIFastqFile]] = None,
    ) -> None:
        self.run_alias = run_alias
        self.experiment = experiment
        self.platform = platform
        self.run_date = run_date
        self.fastqfiles = fastqfiles
        self.run_center = NGIRun.run_center

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        run_date_str = json_obj.get("run_date")
        return cls(
            run_alias=json_obj.get("run_alias"),
            experiment=NGIExperimentBase.from_json(json_obj.get("experiment")),
            platform=NGIIlluminaSequencingPlatform.from_json(json_obj.get("platform")),
            run_date=datetime.datetime.fromisoformat(run_date_str)
            if run_date_str
            else None,
            fastqfiles=[
                NGIFastqFile.from_json(file_json)
                for file_json in json_obj.get("fastqfiles", [])
            ],
        )
