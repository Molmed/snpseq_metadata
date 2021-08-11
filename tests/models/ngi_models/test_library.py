from snpseq_metadata.models.ngi_models import NGILibrary


class TestNGILibrary:
    def test_from_json(self, ngi_library_obj, ngi_library_json):
        library = NGILibrary.from_json(json_obj=ngi_library_json)
        assert library == ngi_library_obj

    def test_to_json(self, ngi_library_obj, ngi_library_json):
        assert ngi_library_obj.to_json() == ngi_library_json
