from snpseq_metadata.models.sra_models import (
    SRAExperiment,
    SRAExperimentRef,
    SRAExperimentSet,
)


class TestSRAExperimentRef:
    def test_from_json(self, sra_experiment_ref_obj, sra_experiment_ref_json):
        experiment_ref = SRAExperimentRef.from_json(json_obj=sra_experiment_ref_json)
        assert experiment_ref == sra_experiment_ref_obj.model_object

    def test_to_json(self, sra_experiment_ref_obj, sra_experiment_ref_json):
        assert sra_experiment_ref_obj.to_json() == sra_experiment_ref_json

    def test_to_manifest(self, sra_experiment_ref_obj, sra_experiment_ref_manifest):
        assert sra_experiment_ref_obj.to_manifest() == sra_experiment_ref_manifest

    def test_to_xml(self, sra_experiment_ref_obj, sra_experiment_ref_xml):
        assert sra_experiment_ref_xml in sra_experiment_ref_obj.to_xml()

    def test___str__(self, sra_experiment_ref_obj):
        assert (
            str(sra_experiment_ref_obj) == sra_experiment_ref_obj.model_object.refname
        )

    def test___eq__(self, sra_experiment_ref_obj):
        other_obj = SRAExperimentRef.create_object(
            experiment_name=str(sra_experiment_ref_obj)
        )
        assert other_obj == sra_experiment_ref_obj
        other_obj = SRAExperimentRef.create_object(
            experiment_name=f"not-equal-to-{str(sra_experiment_ref_obj)}"
        )
        assert other_obj != sra_experiment_ref_obj

    def test_create_object(self, sra_experiment_ref_obj):
        obj = SRAExperimentRef.create_object(
            experiment_name=str(sra_experiment_ref_obj)
        )
        assert obj == sra_experiment_ref_obj

    def test_get_reference(self, sra_experiment_ref_obj):
        assert id(sra_experiment_ref_obj.get_reference()) == id(sra_experiment_ref_obj)


class TestSRAExperiment:
    def test_from_json(self, sra_experiment_obj, sra_experiment_json):
        experiment = SRAExperiment.from_json(json_obj=sra_experiment_json)
        assert experiment == sra_experiment_obj.model_object

    def test_to_json(self, sra_experiment_obj, sra_experiment_json):
        assert sra_experiment_obj.to_json() == sra_experiment_json

    def test_to_manifest(self, sra_experiment_obj, sra_experiment_manifest):
        assert sra_experiment_obj.to_manifest() == sra_experiment_manifest

    def test_to_xml(self, sra_experiment_obj, sra_experiment_xml):
        assert "".join(sra_experiment_xml.split()) in "".join(
            sra_experiment_obj.to_xml().split()
        )

    def test_get_reference(self, sra_experiment_obj, sra_experiment_ref_obj):
        assert sra_experiment_obj.get_reference() == sra_experiment_ref_obj

    def test_create_object(self, sra_experiment_obj):
        obj = SRAExperiment.create_object(
            alias=sra_experiment_obj.model_object.alias,
            title=sra_experiment_obj.model_object.title,
            study_ref=sra_experiment_obj.study_ref,
            library=sra_experiment_obj.library,
            platform=sra_experiment_obj.platform,
        )
        assert obj == sra_experiment_obj


class TestSRAExperimentSet:
    def test_from_json(self, sra_experiment_set_obj, sra_experiment_set_json):
        experiment_set = SRAExperimentSet.from_json(json_obj=sra_experiment_set_json)
        assert experiment_set == sra_experiment_set_obj.model_object

    def test_to_json(self, sra_experiment_set_obj, sra_experiment_set_json):
        assert sra_experiment_set_obj.to_json() == sra_experiment_set_json

    def test_to_manifest(self, sra_experiment_set_obj, sra_experiment_set_manifest):
        assert sra_experiment_set_obj.to_manifest() == sra_experiment_set_manifest

    def test_to_xml(self, sra_experiment_set_obj, sra_experiment_set_xml):
        assert "".join(sra_experiment_set_xml.split()) in "".join(
            sra_experiment_set_obj.to_xml().split()
        )

    def test_restrict_to_study(self, sra_experiment_set_obj, sra_experiment_obj):
        experiment_set = sra_experiment_set_obj.restrict_to_study(
            study_ref=sra_experiment_obj.study_ref
        )
        assert experiment_set.experiments == [sra_experiment_obj]
