from snpseq_metadata.models.lims_models import LIMSSample


class TestLIMSSample:
    def test_from_json(self, lims_sample_json, lims_sample_obj):
        sample = LIMSSample.from_json(json_obj=lims_sample_json)
        assert sample == lims_sample_obj

    def test_to_json(self, lims_sample_json):
        sample = LIMSSample.from_json(json_obj=lims_sample_json)
        assert sample.to_json() == lims_sample_json
