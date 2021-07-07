from snpseq_metadata.models.sra_models import SRASampleDescriptor


class TestSRASampleDescriptor:
    def test_from_json(self, sample_obj, sample_json):
        sample = SRASampleDescriptor.from_json(json_obj=sample_json)
        assert sample == sample_obj.model_object

    def test_to_json(self, sample_obj, sample_json):
        assert sample_obj.to_json() == sample_json

    def test_to_manifest(self, sample_obj, sample_manifest):
        assert sample_obj.to_manifest() == sample_manifest

    def test_to_xml(self, sample_obj, sample_xml):
        assert sample_xml in sample_obj.to_xml()

    def test___str__(self, sample_obj):
        assert str(sample_obj) == sample_obj.model_object.refname

    def test___eq__(self, sample_obj):
        other_obj = SRASampleDescriptor.create_object(refname=str(sample_obj))
        assert other_obj == sample_obj
        other_obj = SRASampleDescriptor.create_object(
            refname=f"not-equal-to-{str(sample_obj)}"
        )
        assert other_obj != sample_obj

    def test_create_object(self, sample_obj):
        obj = SRASampleDescriptor.create_object(refname=str(sample_obj))
        assert obj == sample_obj
