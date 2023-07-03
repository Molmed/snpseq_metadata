from snpseq_metadata.models.sra_models import SRASampleDescriptor


class TestSRASampleDescriptor:
    def test_from_json(self, sra_sample_obj, sra_sample_json):
        sample = SRASampleDescriptor.from_json(json_obj=sra_sample_json)
        assert sample == sra_sample_obj.model_object

    def test_to_json(self, sra_sample_obj, sra_sample_json):
        assert sra_sample_obj.to_json() == sra_sample_json

    def test_to_manifest(self, sra_sample_obj, sra_sample_manifest):
        assert sra_sample_obj.to_manifest() == sra_sample_manifest

    def test_to_xml(self, sra_sample_obj, sra_sample_xml):
        assert sra_sample_obj.to_xml(xml_declaration=False).split() == \
               sra_sample_xml.split()

    def test___getattr__(self, sra_sample_obj, sra_sample_json):
        assert sra_sample_obj.refname == sra_sample_json["refname"]

    def test___str__(self, sra_sample_obj):
        assert str(sra_sample_obj) == sra_sample_obj.refname

    def test___eq__(self, sra_sample_obj):
        other_obj = SRASampleDescriptor.create_object(refname=str(sra_sample_obj))
        assert other_obj == sra_sample_obj
        other_obj = SRASampleDescriptor.create_object(
            refname=f"not-equal-to-{str(sra_sample_obj)}"
        )
        assert other_obj != sra_sample_obj

    def test_create_object(self, sra_sample_obj):
        obj = SRASampleDescriptor.create_object(refname=str(sra_sample_obj))
        assert obj == sra_sample_obj
