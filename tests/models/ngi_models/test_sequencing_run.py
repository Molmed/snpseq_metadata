from snpseq_metadata.models.ngi_models import NGIRun


class TestNGIRun:
    def test_from_json(self, ngi_sequencing_run_obj, ngi_sequencing_run_json):
        run = NGIRun.from_json(json_obj=ngi_sequencing_run_json)
        assert run == ngi_sequencing_run_obj

    def test_to_json(self, ngi_sequencing_run_obj, ngi_sequencing_run_json):
        assert ngi_sequencing_run_obj.to_json() == ngi_sequencing_run_json
