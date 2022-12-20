from typing import ClassVar, List, Optional, TypeVar, Type, Tuple
import datetime
from xsdata.models.datatype import XmlDateTime

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.sra_models.experiment import SRAExperimentBase
from snpseq_metadata.models.sra_models.file_models import SRAFastqFile
from snpseq_metadata.models.xsdata import Run

T = TypeVar("T", bound="SRARun")


class SRARun(SRAMetadataModel):
    model_object_class: ClassVar[Type] = Run

    def __init__(
        self,
        model_object: model_object_class,
        experiment: Optional[SRAExperimentBase] = None,
        fastqfiles: Optional[List[SRAFastqFile]] = None,
    ) -> None:
        super().__init__(model_object=model_object)
        self.experiment = experiment
        self.fastqfiles = fastqfiles

    @classmethod
    def create_object(
        cls: Type[T],
        run_alias: str,
        experiment: SRAExperimentBase,
        run_center: str,
        fastqfiles: List[SRAFastqFile],
        run_date: Optional[datetime.datetime] = None,
    ) -> T:
        xsd_files = Run.DataBlock.Files(
            file=list(map(lambda f: f.model_object, fastqfiles))
        )
        xsd_data_block = Run.DataBlock(files=xsd_files)
        xsd_run_date = XmlDateTime.from_datetime(run_date) if run_date else None
        model_object = cls.model_object_class(
            title=run_alias,
            run_center=run_center,
            run_date=xsd_run_date,
            center_name=run_center,
            experiment_ref=experiment.get_reference().model_object,
            data_block=xsd_data_block
        )
        return cls(
            model_object=model_object,
            experiment=experiment,
            fastqfiles=fastqfiles,
        )

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = []
        for fastqfile in self.fastqfiles:
            manifest.extend(fastqfile.to_manifest())
        return manifest
