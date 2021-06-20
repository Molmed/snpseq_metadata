from snpseq_metadata.models.ngi_models import NGIRun, NGIExperimentRef


class TestNGIRun:
    def test_to_json(self):
        run_alias = "this-is-a-run-alias"
        run_center = "National Genomics Infrastructure, Uppsala"
        experiment_name = "this-is-an-experiment-ref"
        sample_project = "this-is-a-sample-project"
        sample_id = "this-is-a-sample-id"
        experiment_ref = NGIExperimentRef(
            experiment_name=experiment_name,
            project_id=sample_project,
            sample_id=sample_id,
        )
        run = NGIRun(run_alias=run_alias, experiment_ref=experiment_ref)
