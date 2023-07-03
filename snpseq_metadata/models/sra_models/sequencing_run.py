from typing import ClassVar, List, Optional, TypeVar, Type, Tuple, Union
import datetime
from xsdata.models.datatype import XmlDateTime

from snpseq_metadata.models.sra_models.attribute import SRAAttribute
from snpseq_metadata.models.sra_models.experiment import SRAExperimentBase, SRAExperimentRef, \
    SRAExperiment
from snpseq_metadata.models.sra_models.file_models import SRAFastqFile
from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import Run

T = TypeVar("T", bound="SRARun")
X = TypeVar("X", None, str, List[SRAAttribute], List[SRAFastqFile], SRAExperimentBase)


class SRARun(SRAMetadataModel):
    model_object_class: ClassVar[Type] = Run

    def __getattr__(self, item: str) -> X:
        attr = super().__getattr__(item)
        if attr:
            return attr
        if item == "fastqfiles":
            attr = getattr(self.model_object, "data_block")
            return [
                SRAFastqFile.from_model_object(model_object=file_model)
                for file_model in attr.files.file]
        if item in ["experiment", "experiment_ref"]:
            attr = getattr(self.model_object, "experiment_ref")
            return SRAExperimentRef.from_model_object(model_object=attr) \
                   or SRAExperiment.from_model_object(model_object=attr)
        attr = getattr(self.model_object, item)
        if type(attr) == Run.RunAttributes:
            return [
                SRAAttribute.from_model_object(run_attribute)
                for run_attribute in attr.run_attribute]

    @classmethod
    def create_object(
        cls: Type[T],
        run_alias: str,
        experiment: SRAExperimentBase,
        run_center: str,
        fastqfiles: List[SRAFastqFile],
        run_attributes: Optional[List[SRAAttribute]] = None,
        run_date: Optional[datetime.datetime] = None,
    ) -> T:
        xsd_files = Run.DataBlock.Files(
            file=list(map(lambda f: f.model_object, fastqfiles))
        )
        xsd_data_block = Run.DataBlock(files=xsd_files)
        xsd_run_date = XmlDateTime.from_datetime(run_date) if run_date else None
        xsd_run_attributes = Run.RunAttributes(
            run_attribute=[
                run_attribute.model_object for run_attribute in run_attributes]
        ) if run_attributes else None
        model_object = cls.model_object_class(
            title=run_alias,
            run_center=run_center,
            run_date=xsd_run_date,
            center_name=run_center,
            experiment_ref=experiment.get_reference().model_object,
            data_block=xsd_data_block,
            run_attributes=xsd_run_attributes
        )
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = []
        for fastqfile in self.fastqfiles:
            manifest.extend(fastqfile.to_manifest())
        return manifest

    def is_project(self, project_id: str) -> Optional[bool]:
        for run_attribute in self.run_attributes or []:
            if run_attribute.tag == "project_id":
                return run_attribute.value == project_id

    def is_sample(self, sample_id: str) -> Optional[bool]:
        for run_attribute in self.run_attributes or []:
            if run_attribute.tag == "sample_id":
                return run_attribute.value == sample_id
