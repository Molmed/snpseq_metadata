from snpseq_metadata.models.ngi_models import NGILibrary


class TestNGILibrary:
    def test_from_json(self, library_obj, library_json):
        library = NGILibrary.from_json(json_obj=library_json)
        assert library == library_obj

    def test_to_json(self, library_obj, library_json):
        assert library_obj.to_json() == library_json
