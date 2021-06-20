from snpseq_metadata.models.ngi_models import NGIExperimentRef

import tests.models.ngi_models.test_flowcell


class TestNGIExperimentRef:
    def test_from_samplesheet_row(self):
        samplesheet_data = (
            tests.models.ngi_models.test_flowcell.TestFlowcell._return_samplesheet_data()
        )
        for samplesheet_row in samplesheet_data:
            experiment = NGIExperimentRef.from_samplesheet_row(samplesheet_row)
            assert (
                experiment.experiment_name
                == samplesheet_row["description"].split(":")[-1]
            )
            assert experiment.project_id == samplesheet_row["sample_project"]
            assert experiment.sample_id == samplesheet_row["sample_id"]
