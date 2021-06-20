import pytest
from snpseq_metadata.models.lims_models import LIMSSequencingContainer


@pytest.fixture
def sequencing_container_json():
    return {"name": "this-is-a-sequencing-container-name", "samples": []}


class TestLIMSSequencingContainer:
    def test_from_json(self, sequencing_container_json):
        sequencing_container = LIMSSequencingContainer.from_json(
            json_obj=sequencing_container_json
        )
        assert sequencing_container.name == sequencing_container_json["name"]
        assert sequencing_container.samples == sequencing_container_json["samples"]

    def test_to_json(self, sequencing_container_json):
        sequencing_container = LIMSSequencingContainer.from_json(
            json_obj=sequencing_container_json
        )
        assert sequencing_container.to_json() == sequencing_container_json
