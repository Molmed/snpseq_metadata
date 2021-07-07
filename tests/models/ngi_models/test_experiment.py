from snpseq_metadata.models.ngi_models import (
    NGIExperimentRef,
    NGIExperiment,
    NGIExperimentBase,
    NGIExperimentSet,
)


class TestNGIExperimentBase:
    def test_experiment_ref_from_json(self, experiment_ref_obj, experiment_ref_json):
        experiment_ref = NGIExperimentBase.from_json(json_obj=experiment_ref_json)
        assert isinstance(experiment_ref, NGIExperimentRef)
        assert experiment_ref == experiment_ref_obj

    def test_experiment_from_json(self, experiment_obj, experiment_json):
        experiment = NGIExperimentBase.from_json(json_obj=experiment_json)
        assert isinstance(experiment, NGIExperiment)
        assert experiment == experiment_obj

    def test_is_reference_to(self, experiment_ref_obj, experiment_obj):
        assert experiment_ref_obj.is_reference_to(experiment_obj)
        assert not experiment_obj.is_reference_to(experiment_ref_obj)


class TestNGIExperimentRef:
    def test_from_samplesheet_row(
        self, samplesheet_row, illumina_platform_obj, experiment_ref_obj
    ):
        experiment_ref = NGIExperimentRef.from_samplesheet_row(
            samplesheet_row=samplesheet_row, platform=illumina_platform_obj
        )
        experiment_ref_obj.alias = f"{experiment_ref_obj.project.project_id}-{experiment_ref_obj.sample.sample_id}-{illumina_platform_obj.model_name}"
        assert experiment_ref == experiment_ref_obj

    def test_from_json(self, experiment_ref_obj, experiment_ref_json):
        experiment_ref = NGIExperimentRef.from_json(experiment_ref_json)
        assert experiment_ref == experiment_ref_obj

    def test_to_json(self, experiment_ref_obj, experiment_ref_json):
        assert experiment_ref_obj.to_json() == experiment_ref_json

    def test_get_reference(self, experiment_ref_obj):
        assert experiment_ref_obj.get_reference() == experiment_ref_obj


class TestNGIExperiment:
    def test_from_json(self, experiment_obj, experiment_json):
        experiment = NGIExperiment.from_json(experiment_json)
        assert experiment == experiment_obj

    def test_to_json(self, experiment_obj, experiment_json):
        assert experiment_obj.to_json() == experiment_json

    def test_get_reference(self, experiment_obj, experiment_ref_obj):
        assert experiment_obj.get_reference() == experiment_ref_obj


class TestNGIExperimentSet:
    def test_from_json(self, experiment_set_obj, experiment_set_json):
        experiment_set = NGIExperimentSet.from_json(experiment_set_json)
        assert experiment_set == experiment_set_obj

    def test_to_json(self, experiment_set_obj, experiment_set_json):
        assert experiment_set_obj.to_json() == experiment_set_json

    def test_get_experiment_for_reference(
        self, experiment_set_obj, experiment_ref_obj, experiment_obj
    ):
        experiment = experiment_set_obj.get_experiment_for_reference(
            experiment_ref=experiment_ref_obj
        )
        assert experiment == experiment_obj
