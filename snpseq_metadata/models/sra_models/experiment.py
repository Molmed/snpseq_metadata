from typing import ClassVar, List, Type, TypeVar, Optional, Tuple

from snpseq_metadata.models.sra_models.sequencing_platform import (
    SRASequencingPlatform,
)
from snpseq_metadata.models.sra_models.library import SRALibrary
from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.sra_models.study import SRAStudyRef
from snpseq_metadata.models.xsdata import (
    RefObjectType,
    RunType as Run,
    Experiment,
    ExperimentType as XSDExperiment,
    ExperimentSet as XSDExperimentSet,
)

TR = TypeVar("TR", bound="SRAExperimentRef")
T = TypeVar("T", bound="SRAExperiment")
TS = TypeVar("TS", bound="SRAExperimentSet")
TB = TypeVar("TB", bound="SRAExperimentBase")


class SRAExperimentBase(SRAMetadataModel):
    model_object_class: ClassVar[Type]

    def get_reference(self) -> TR:
        raise NotImplementedError

    def to_manifest(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @classmethod
    def create_object(cls: Type[TB], *args, **kwargs) -> TB:
        raise NotImplementedError


class SRAExperimentRef(SRAExperimentBase):
    model_object_class: ClassVar[Type] = RefObjectType
    model_object_parent_field: ClassVar[Optional[Tuple[Type, str]]] = (Run, "experiment_ref")

    def __str__(self) -> str:
        return self.model_object.refname

    @classmethod
    def create_object(cls: Type[TR], experiment_name: str) -> TR:
        model_object = cls.model_object_class(refname=experiment_name)
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [("NAME", self.model_object.refname)]

    def is_reference_to(self, other: T) -> bool:
        return all(
            [
                isinstance(other, SRAExperiment),
                self.model_object.refname == other.model_object.alias,
            ]
        )

    def get_reference(self) -> TR:
        return self


class SRAExperiment(SRAExperimentBase):
    model_object_class: ClassVar[Type] = XSDExperiment
    model_object_meta_class: ClassVar[Optional[Type]] = Experiment

    def __init__(
        self,
        model_object: model_object_class,
        study_ref: Optional[SRAStudyRef] = None,
        platform: Optional[SRASequencingPlatform] = None,
        library: Optional[SRALibrary] = None,
    ):
        super().__init__(model_object)
        self.study_ref = study_ref
        self.platform = platform
        self.library = library

    @classmethod
    def create_object(
        cls: Type[T],
        alias: str,
        title: str,
        study_ref: SRAStudyRef,
        platform: SRASequencingPlatform,
        library: SRALibrary,
    ) -> T:
        model_object = cls.model_object_class(
            title=title,
            alias=alias,
            study_ref=study_ref.model_object,
            platform=platform.model_object,
            design=library.model_object,
        )
        return cls(
            model_object=model_object,
            study_ref=study_ref,
            platform=platform,
            library=library,
        )

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = [("NAME", self.model_object.alias)]
        manifest.extend(self.study_ref.to_manifest())
        manifest.extend(self.platform.to_manifest())
        manifest.extend(self.library.to_manifest())
        return manifest

    def get_reference(self) -> SRAExperimentRef:
        return SRAExperimentRef.create_object(experiment_name=self.model_object.alias)


class SRAExperimentSet(SRAMetadataModel):
    model_object_class: ClassVar[Type] = XSDExperimentSet

    def __init__(
        self,
        model_object: model_object_class,
        experiments: Optional[List[SRAExperiment]] = None,
    ):
        super().__init__(model_object)
        self.experiments = experiments

    @classmethod
    def create_object(cls: Type[TS], experiments: List[SRAExperiment]) -> TS:
        model_object = cls.model_object_class(
            experiment=[experiment.model_object for experiment in experiments]
        )
        return cls(model_object=model_object, experiments=experiments)

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = []
        for experiment in self.experiments:
            manifest.extend(experiment.to_manifest())
        return manifest

    def restrict_to_study(self, study_ref: SRAStudyRef) -> TS:
        experiments = list(
            filter(lambda exp: study_ref == exp.study_ref, self.experiments)
        )
        return self.create_object(experiments=experiments)
