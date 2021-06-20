from typing import Dict, List, Type, TypeVar, Optional

from snpseq_metadata.models.ngi_models.sequencing_platform import (
    NGIIlluminaSequencingPlatform,
)
from snpseq_metadata.models.ngi_models.library import NGILibrary
from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.models.ngi_models.study import NGIStudyRef
from snpseq_metadata.models.ngi_models.sample import NGISampleDescriptor

T = TypeVar("T", bound="NGIExperiment")
TB = TypeVar("TB", bound="NGIExperimentBase")
TR = TypeVar("TR", bound="NGIExperimentRef")
TS = TypeVar("TS", bound="NGIExperimentSet")


class NGIExperimentBase(NGIMetadataModel):
    def __init__(self, alias: str, project: NGIStudyRef) -> None:
        self.alias = alias
        self.project = project

    @classmethod
    def from_json(cls: Type[TB], json_obj: Dict) -> TB:
        if "sample" in json_obj:
            return NGIExperimentRef.from_json(json_obj=json_obj)
        else:
            return NGIExperiment.from_json(json_obj=json_obj)

    def is_reference_to(self, other: T) -> bool:
        return all(
            [
                isinstance(self, NGIExperimentRef),
                isinstance(other, NGIExperiment),
                self.alias == other.alias,
            ]
        )

    def get_reference(self) -> TR:
        raise NotImplementedError


class NGIExperimentRef(NGIExperimentBase):
    def __init__(
        self, alias: str, project: NGIStudyRef, sample: NGISampleDescriptor
    ) -> None:
        super().__init__(alias, project)
        self.sample = sample

    @classmethod
    def from_samplesheet_row(
        cls: Type[TR], samplesheet_row: Dict, platform: NGIIlluminaSequencingPlatform
    ) -> TR:
        project_id = samplesheet_row.get("sample_project")
        sample_id = samplesheet_row.get("sample_id")
        alias = f"{project_id}-{sample_id}-{platform.model_name}"
        return cls(
            alias=alias,
            project=NGIStudyRef(project_id=project_id),
            sample=NGISampleDescriptor(sample_id=sample_id),
        )

    @classmethod
    def from_json(cls: Type[TR], json_obj: Dict) -> TR:
        return cls(
            alias=json_obj.get("alias"),
            project=NGIStudyRef.from_json(json_obj.get("project")),
            sample=NGISampleDescriptor.from_json(json_obj.get("sample")),
        )

    def get_reference(self) -> TR:
        return self


class NGIExperiment(NGIExperimentBase):
    def __init__(
        self,
        alias: str,
        title: str,
        project: NGIStudyRef,
        platform: NGIIlluminaSequencingPlatform,
        library: NGILibrary,
    ) -> None:
        super().__init__(alias, project)
        self.title = title
        self.platform = platform
        self.library = library

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        project = NGIStudyRef.from_json(json_obj=json_obj.get("project"))
        platform = NGIIlluminaSequencingPlatform.from_json(
            json_obj=json_obj.get("platform")
        )
        library = NGILibrary.from_json(json_obj=json_obj.get("library"))
        return cls(
            alias=json_obj.get("alias"),
            title=json_obj.get("title"),
            project=project,
            platform=platform,
            library=library,
        )

    def get_reference(self) -> NGIExperimentRef:
        return NGIExperimentRef(
            alias=self.alias, project=self.project, sample=self.library.sample
        )


class NGIExperimentSet(NGIMetadataModel):
    def __init__(self, experiments: List[NGIExperiment]) -> None:
        self.experiments = experiments

    @classmethod
    def from_json(cls: Type[TS], json_obj: Dict) -> TS:
        experiments = [
            NGIExperiment.from_json(exp) for exp in json_obj.get("experiments", [])
        ]
        return cls(experiments=experiments)

    def get_experiment_for_reference(
        self, experiment_ref: NGIExperimentRef
    ) -> Optional[NGIExperiment]:
        try:
            return next(
                filter(
                    lambda exp: experiment_ref.is_reference_to(exp), self.experiments
                )
            )
        except StopIteration:
            pass
