from snpseq_metadata.models.sra_models import SRAStudyRef


class TestSRAStudyRef:
    def test_from_json(self, sra_study_obj, sra_study_json):
        study = SRAStudyRef.from_json(json_obj=sra_study_json)
        assert study == sra_study_obj.model_object

    def test_to_json(self, sra_study_obj, sra_study_json):
        assert sra_study_obj.to_json() == sra_study_json

    def test_to_manifest(self, sra_study_obj, sra_study_manifest):
        assert sra_study_obj.to_manifest() == sra_study_manifest

    def test_to_xml(self, sra_study_obj, sra_study_xml):
        assert sra_study_obj.to_xml(xml_declaration=False).split() == \
               sra_study_xml.split()

    def test___getattr__(self, sra_study_obj, sra_study_json):
        assert sra_study_obj.refname == sra_study_json["refname"]

    def test___str__(self, sra_study_obj):
        assert str(sra_study_obj) == sra_study_obj.refname

    def test___eq__(self, sra_study_obj):
        other_obj = SRAStudyRef.create_object(refname=str(sra_study_obj))
        assert other_obj == sra_study_obj
        other_obj = SRAStudyRef.create_object(
            refname=f"not-equal-to-{str(sra_study_obj)}"
        )
        assert other_obj != sra_study_obj

    def test_create_object(self, sra_study_obj):
        obj = SRAStudyRef.create_object(refname=str(sra_study_obj))
        assert obj == sra_study_obj
