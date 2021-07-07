from snpseq_metadata.models.ngi_models import NGISampleDescriptor


class TestNGISampleDescriptor:
    def test_from_json(self, sample_obj, sample_json):
        sample = NGISampleDescriptor.from_json(json_obj=sample_json)
        assert sample == sample_obj

    def test_to_json(self, sample_obj, sample_json):
        assert sample_obj.to_json() == sample_json
