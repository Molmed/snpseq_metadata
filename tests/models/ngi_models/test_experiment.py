from snpseq_metadata.models.ngi_models import (
    NGIExperimentRef,
    NGIExperiment,
    NGIExperimentBase,
    NGIExperimentSet,
)


class TestNGIExperimentBase:
    def test_experiment_ref_from_json(
        self, ngi_experiment_ref_obj, ngi_experiment_ref_json
    ):
        experiment_ref = NGIExperimentBase.from_json(json_obj=ngi_experiment_ref_json)
        assert isinstance(experiment_ref, NGIExperimentRef)
        assert experiment_ref == ngi_experiment_ref_obj

    def test_experiment_from_json(self, ngi_experiment_obj, ngi_experiment_json):
        experiment = NGIExperimentBase.from_json(json_obj=ngi_experiment_json)
        assert isinstance(experiment, NGIExperiment)
        assert experiment == ngi_experiment_obj

    def test_is_reference_to(self, ngi_experiment_ref_obj, ngi_experiment_obj):
        assert ngi_experiment_ref_obj.is_reference_to(ngi_experiment_obj)
        assert not ngi_experiment_obj.is_reference_to(ngi_experiment_ref_obj)


class TestNGIExperimentRef:
    def test_from_samplesheet_row(
        self, samplesheet_row, ngi_illumina_platform_obj, ngi_experiment_ref_obj
    ):
        experiment_ref = NGIExperimentRef.from_samplesheet_row(
            samplesheet_row=samplesheet_row, platform=ngi_illumina_platform_obj
        )
        ngi_experiment_ref_obj.alias = f"{ngi_experiment_ref_obj.project.project_id}-{ngi_experiment_ref_obj.sample.sample_id}-{ngi_illumina_platform_obj.model_name}"
        assert experiment_ref == ngi_experiment_ref_obj

    def test_from_json(self, ngi_experiment_ref_obj, ngi_experiment_ref_json):
        experiment_ref = NGIExperimentRef.from_json(ngi_experiment_ref_json)
        assert experiment_ref == ngi_experiment_ref_obj

    def test_to_json(self, ngi_experiment_ref_obj, ngi_experiment_ref_json):
        assert ngi_experiment_ref_obj.to_json() == ngi_experiment_ref_json

    def test_get_reference(self, ngi_experiment_ref_obj):
        assert ngi_experiment_ref_obj.get_reference() == ngi_experiment_ref_obj


class TestNGIExperiment:
    def test_from_json(self, ngi_experiment_obj, ngi_experiment_json):
        experiment = NGIExperiment.from_json(ngi_experiment_json)
        assert experiment == ngi_experiment_obj

    def test_to_json(self, ngi_experiment_obj, ngi_experiment_json):
        assert ngi_experiment_obj.to_json() == ngi_experiment_json

    def test_get_reference(self, ngi_experiment_obj, ngi_experiment_ref_obj):
        assert ngi_experiment_obj.get_reference() == ngi_experiment_ref_obj


class TestNGIExperimentSet:
    def test_from_json(self, ngi_experiment_set_obj, ngi_experiment_set_json):
        experiment_set = NGIExperimentSet.from_json(ngi_experiment_set_json)
        assert experiment_set == ngi_experiment_set_obj

    def test_to_json(self, ngi_experiment_set_obj, ngi_experiment_set_json):
        assert ngi_experiment_set_obj.to_json() == ngi_experiment_set_json

    def test_get_experiment_for_reference(
        self, ngi_experiment_set_obj, ngi_experiment_ref_obj, ngi_experiment_obj
    ):
        experiment = ngi_experiment_set_obj.get_experiment_for_reference(
            experiment_ref=ngi_experiment_ref_obj
        )
        assert experiment == ngi_experiment_obj
