from snpseq_metadata.models.sra_models import (
    SRAExperiment,
    SRAExperimentRef,
    SRAExperimentSet,
)


class TestSRAExperimentRef:
    def test_from_json(self, experiment_ref_obj, experiment_ref_json):
        experiment_ref = SRAExperimentRef.from_json(json_obj=experiment_ref_json)
        assert experiment_ref == experiment_ref_obj.model_object

    def test_to_json(self, experiment_ref_obj, experiment_ref_json):
        assert experiment_ref_obj.to_json() == experiment_ref_json

    def test_to_manifest(self, experiment_ref_obj, experiment_ref_manifest):
        assert experiment_ref_obj.to_manifest() == experiment_ref_manifest

    def test_to_xml(self, experiment_ref_obj, experiment_ref_xml):
        assert experiment_ref_xml in experiment_ref_obj.to_xml()

    def test___str__(self, experiment_ref_obj):
        assert str(experiment_ref_obj) == experiment_ref_obj.model_object.refname

    def test___eq__(self, experiment_ref_obj):
        other_obj = SRAExperimentRef.create_object(
            experiment_name=str(experiment_ref_obj)
        )
        assert other_obj == experiment_ref_obj
        other_obj = SRAExperimentRef.create_object(
            experiment_name=f"not-equal-to-{str(experiment_ref_obj)}"
        )
        assert other_obj != experiment_ref_obj

    def test_create_object(self, experiment_ref_obj):
        obj = SRAExperimentRef.create_object(experiment_name=str(experiment_ref_obj))
        assert obj == experiment_ref_obj

    def test_get_reference(self, experiment_ref_obj):
        assert id(experiment_ref_obj.get_reference()) == id(experiment_ref_obj)


class TestSRAExperiment:
    def test_from_json(self, experiment_obj, experiment_json):
        experiment = SRAExperiment.from_json(json_obj=experiment_json)
        assert experiment == experiment_obj.model_object

    def test_to_json(self, experiment_obj, experiment_json):
        assert experiment_obj.to_json() == experiment_json

    def test_to_manifest(self, experiment_obj, experiment_manifest):
        assert experiment_obj.to_manifest() == experiment_manifest

    def test_to_xml(self, experiment_obj, experiment_xml):
        exp = "".join(experiment_xml.split())
        obs = "".join(experiment_obj.to_xml().split())
        assert exp in obs

    def test_get_reference(self, experiment_obj, experiment_ref_obj):
        assert experiment_obj.get_reference() == experiment_ref_obj

    def test_create_object(self, experiment_obj):
        obj = SRAExperiment.create_object(
            alias=experiment_obj.model_object.alias,
            title=experiment_obj.model_object.title,
            study_ref=experiment_obj.study_ref,
            library=experiment_obj.library,
            platform=experiment_obj.platform,
        )
        assert obj == experiment_obj


class TestSRAExperimentSet:
    pass
