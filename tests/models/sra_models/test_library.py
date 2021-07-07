from snpseq_metadata.models.sra_models import SRALibrary


class TestSRALibrary:
    def test_from_json(self, library_obj, library_json):
        library = SRALibrary.from_json(json_obj=library_json)
        assert library == library_obj.model_object

    def test_to_json(self, library_obj, library_json):
        assert library_obj.to_json() == library_json

    def test_to_manifest(self, library_obj, library_manifest):
        assert library_obj.to_manifest() == library_manifest

    def test_to_xml(self, library_obj, library_xml):
        assert "".join(library_xml.split()) in "".join(library_obj.to_xml().split())

    def test_create_object(self, library_obj, library_json, sample_obj):
        library = SRALibrary.create_object(
            sample=sample_obj,
            description=library_json["DESIGN_DESCRIPTION"],
            strategy=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"],
            source=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"],
            selection=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"],
            is_paired=list(library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_LAYOUT"].keys())[
                0
            ]
            == "PAIRED",
        )
        assert library == library_obj
