from snpseq_metadata.models.sra_models import SRALibrary


class TestSRALibrary:
    def test_from_json(self, sra_library_obj, sra_library_json):
        library = SRALibrary.from_json(json_obj=sra_library_json)
        assert library == sra_library_obj.model_object

    def test_to_json(self, sra_library_obj, sra_library_json):
        assert sra_library_obj.to_json() == sra_library_json

    def test_to_manifest(self, sra_library_obj, sra_library_manifest):
        assert sra_library_obj.to_manifest() == sra_library_manifest

    def test_to_xml(self, sra_library_obj, sra_library_xml):
        assert sra_library_obj.to_xml(xml_declaration=False).split() == \
               sra_library_xml.split()

    def test_create_object(self, sra_library_obj, sra_library_json, sra_sample_obj):
        library = SRALibrary.create_object(
            sample=sra_sample_obj,
            description=sra_library_json["DESIGN_DESCRIPTION"],
            strategy=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"],
            source=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"],
            selection=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"],
            is_paired=list(
                sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_LAYOUT"].keys()
            )[0]
            == "PAIRED",
        )
        assert library == sra_library_obj
