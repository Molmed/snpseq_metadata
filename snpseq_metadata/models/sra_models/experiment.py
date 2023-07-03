from typing import ClassVar, List, Type, TypeVar, Optional, Tuple, Union

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
    ExperimentSet as XSDExperimentSet,
)

TR = TypeVar("TR", bound="SRAExperimentRef")
T = TypeVar("T", bound="SRAExperiment")
TS = TypeVar("TS", bound="SRAExperimentSet")
TB = TypeVar("TB", bound="SRAExperimentBase")
X = TypeVar("X", "None", "str", "SRAStudyRef", "SRALibrary", "SRASequencingPlatform")


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
        return self.refname

    @classmethod
    def create_object(cls: Type[TR], experiment_name: str) -> TR:
        model_object = cls.model_object_class(refname=experiment_name)
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [("NAME", self.refname)]

    def is_reference_to(self, other: T) -> bool:
        return all(
            [
                isinstance(other, SRAExperiment),
                self.refname == other.alias,
            ]
        )

    def get_reference(self) -> TR:
        return self


class SRAExperiment(SRAExperimentBase):
    model_object_class: ClassVar[Type] = Experiment

    def __getattr__(self, item: str) -> X:
        attr = super().__getattr__(item)
        if attr:
            return attr
        if item in ["project", "study_ref"]:
            return SRAStudyRef(model_object=self.model_object.study_ref)
        if item == "library":
            return SRALibrary.from_model_object(self.model_object.design)
        if item == "platform":
            return SRASequencingPlatform.from_model_object(model_object=self.model_object.platform)

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
            model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = [("NAME", self.alias)]
        manifest.extend(self.project.to_manifest())
        manifest.extend(self.platform.to_manifest())
        manifest.extend(self.library.to_manifest())
        return manifest

    def get_reference(self) -> SRAExperimentRef:
        return SRAExperimentRef.create_object(experiment_name=self.alias)


class SRAExperimentSet(SRAMetadataModel):
    model_object_class: ClassVar[Type] = XSDExperimentSet

    def __getattr__(self, item: str) -> Union[None, str, List[SRAExperimentBase]]:
        attr = super().__getattr__(item)
        if attr:
            return attr
        if item in ["experiment", "experiments"]:
            experiments = []
            for experiment_model in self.model_object.experiment:
                experiments.append(
                    SRAExperiment.from_model_object(experiment_model) or
                    SRAExperimentRef.from_model_object(experiment_model))
            return experiments

    @classmethod
    def create_object(cls: Type[TS], experiments: List[SRAExperiment]) -> TS:
        model_object = cls.model_object_class(
            experiment=[experiment.model_object for experiment in experiments]
        )
        return cls(model_object=model_object)

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
