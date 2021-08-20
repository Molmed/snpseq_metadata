from snpseq_metadata.models.lims_models import LIMSSequencingContainer


class TestLIMSSequencingContainer:
    def test_from_json(
        self, lims_sequencing_container_json, lims_sequencing_container_obj
    ):
        sequencing_container = LIMSSequencingContainer.from_json(
            json_obj=lims_sequencing_container_json
        )
        assert sequencing_container == lims_sequencing_container_obj

    def test_to_json(
        self, lims_sequencing_container_json, lims_sequencing_container_obj
    ):
        assert lims_sequencing_container_obj.to_json() == lims_sequencing_container_json
