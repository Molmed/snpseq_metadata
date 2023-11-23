from snpseq_metadata.models.sra_models import SRALibrary, SRALibraryLayout


class TestSRALibraryLayout:

    def test_from_json(self, sra_library_layout_obj, sra_library_layout_json):
        layout = SRALibraryLayout.from_json(json_obj=sra_library_layout_json)
        assert layout == sra_library_layout_obj.model_object

    def test_to_json(self, sra_library_layout_obj, sra_library_layout_json):
        assert sra_library_layout_obj.to_json() == sra_library_layout_json

    def test_to_xml(self, sra_library_layout_obj, sra_library_layout_xml):
        xml_from_obj = sra_library_layout_obj.to_xml(xml_declaration=False)
        assert xml_from_obj.split() == \
               sra_library_layout_xml.split()

    def test_create_object(
            self,
            test_values,
            sra_library_layout_json,
            sra_library_layout_obj
    ):
        is_paired = "PAIRED" in sra_library_layout_json
        fragment_size = test_values.get("udf_fragment_size")
        fragment_lower = test_values.get("udf_fragment_lower")
        fragment_upper = test_values.get("udf_fragment_upper")
        layout = SRALibraryLayout.create_object(
            is_paired=is_paired,
            fragment_size=fragment_size,
            fragment_lower=fragment_lower,
            fragment_upper=fragment_upper
        )
        assert layout == sra_library_layout_obj


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

    def test_create_object(
            self,
            sra_library_obj,
            sra_library_json,
            sra_library_layout_obj,
            sra_sample_obj
    ):
        library = SRALibrary.create_object(
            sample=sra_sample_obj,
            description=sra_library_json["DESIGN_DESCRIPTION"],
            strategy=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"],
            source=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"],
            selection=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"],
            layout=sra_library_layout_obj,
        )
        assert library == sra_library_obj
