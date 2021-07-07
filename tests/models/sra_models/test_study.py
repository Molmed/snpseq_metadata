from snpseq_metadata.models.sra_models import SRAStudyRef


class TestSRAStudyRef:
    def test_from_json(self, study_obj, study_json):
        study = SRAStudyRef.from_json(json_obj=study_json)
        assert study == study_obj.model_object

    def test_to_json(self, study_obj, study_json):
        assert study_obj.to_json() == study_json

    def test_to_manifest(self, study_obj, study_manifest):
        assert study_obj.to_manifest() == study_manifest

    def test_to_xml(self, study_obj, study_xml):
        assert study_xml in study_obj.to_xml()

    def test___str__(self, study_obj):
        assert str(study_obj) == study_obj.model_object.refname

    def test___eq__(self, study_obj):
        other_obj = SRAStudyRef.create_object(refname=str(study_obj))
        assert other_obj == study_obj
        other_obj = SRAStudyRef.create_object(refname=f"not-equal-to-{str(study_obj)}")
        assert other_obj != study_obj

    def test_create_object(self, study_obj):
        obj = SRAStudyRef.create_object(refname=str(study_obj))
        assert obj == study_obj
