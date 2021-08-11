from snpseq_metadata.models.ngi_models import NGISampleDescriptor


class TestNGISampleDescriptor:
    def test_from_json(self, ngi_sample_obj, ngi_sample_json):
        sample = NGISampleDescriptor.from_json(json_obj=ngi_sample_json)
        assert sample == ngi_sample_obj

    def test_to_json(self, ngi_sample_obj, ngi_sample_json):
        assert ngi_sample_obj.to_json() == ngi_sample_json
