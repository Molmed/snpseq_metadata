from typing import ClassVar, List, Type, TypeVar, Optional, Tuple

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.sra_models.sequencing_run import SRARun
from snpseq_metadata.models.sra_models.experiment import SRAExperiment, SRAExperimentSet

from snpseq_metadata.models.xsdata import RunSet

T = TypeVar("T", bound="SRARunSet")


class SRARunSet(SRAMetadataModel):
    model_object_class: ClassVar[Type] = RunSet

    def __init__(
        self, model_object: model_object_class, runs: Optional[List[SRARun]] = None
    ):
        super().__init__(model_object=model_object)
        self.runs = runs

    @classmethod
    def create_object(cls: Type[T], runs: List[SRARun]) -> T:
        model_object = cls.model_object_class(run=[r.model_object for r in runs])
        return cls(model_object=model_object, runs=runs)

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = []
        for run in self.runs:
            manifest.extend(run.to_manifest())
        return manifest

    def restrict_to_experiments(self, experiments: SRAExperimentSet) -> T:
        runs = []
        for experiment in experiments.experiments:
            run = self.get_sequencing_run_for_experiment(experiment=experiment)
            if run:
                run.experiment = experiment
                runs.append(run)
        return self.create_object(runs=runs)

    def get_sequencing_run_for_experiment(
        self, experiment: SRAExperiment
    ) -> Optional[SRARun]:
        try:
            return next(
                filter(
                    lambda run: run.experiment.get_reference().is_reference_to(
                        experiment
                    ),
                    self.runs,
                )
            )
        except StopIteration:
            pass
