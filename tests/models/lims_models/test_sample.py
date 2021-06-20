import pytest

from snpseq_metadata.models.lims_models import LIMSSample


@pytest.fixture
def sample_json():
    return {
        "name": "this-is-a-sample-name",
        "project": "this-is-a-project-name",
        "udf_value_A": "this-is-a-udf-value",
        "udf_value_B": "this-is-another-udf-value",
        "udf_keyvalue": "this-is-yet-another-udf-value",
    }


class TestLIMSSample:
    def test_from_json(self, sample_json):
        sample = LIMSSample.from_json(json_obj=sample_json)
        assert sample.sample_id == sample_json["name"]
        assert sample.project_id == sample_json["project"]
        assert sample.udf == {
            k: v for k, v in sample_json.items() if k not in ["name", "project"]
        }

    def test_to_json(self, sample_json):
        sample = LIMSSample.from_json(json_obj=sample_json)
        assert sample.to_json() == sample_json
