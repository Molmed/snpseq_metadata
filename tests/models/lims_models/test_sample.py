from snpseq_metadata.models.lims_models import LIMSSample


class TestLIMSSample:
    def test_from_json(self, lims_sample_json, lims_sample_obj):
        sample = LIMSSample.from_json(json_obj=lims_sample_json)
        assert sample == lims_sample_obj

    def test_to_json(self, lims_sample_json):
        sample = LIMSSample.from_json(json_obj=lims_sample_json)
        assert sample.to_json() == lims_sample_json

    def test_is_paired(self, lims_sample_obj):
        expected_results = {
            "151x2": True,
            "151+8+8+151": True,
            "151x1": False,
            "151+8": False,
            None: None,
        }
        for read_length, is_paired in expected_results.items():
            setattr(lims_sample_obj, "udf_read_length", read_length)
            assert lims_sample_obj.is_paired() == is_paired
