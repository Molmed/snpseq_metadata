from snpseq_metadata.models.ngi_models import NGIRun


class TestNGIRun:
    def test_from_json(self, run_obj, run_json):
        run = NGIRun.from_json(json_obj=run_json)
        assert run == run_obj

    def test_to_json(self, run_obj, run_json):
        assert run_obj.to_json() == run_json
