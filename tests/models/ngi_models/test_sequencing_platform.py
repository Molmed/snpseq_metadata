import pytest

from snpseq_metadata.exceptions import InstrumentModelNotRecognizedException
from snpseq_metadata.models.ngi_models import (
    NGISequencingPlatform,
    NGIIlluminaSequencingPlatform,
)


class TestNGISequencingPlatform:
    def test_from_json(self, platform_obj, platform_json):
        platform = NGISequencingPlatform.from_json(json_obj=platform_json)
        assert platform == platform_obj

    def test_to_json(self, platform_obj, platform_json):
        assert platform_obj.to_json() == platform_json


class TestNGIIlluminaSequencingPlatform:
    def test_model_name_from_id(self, model_prefixes):
        for model_id, model_name in model_prefixes.items():
            assert (
                NGIIlluminaSequencingPlatform.model_name_from_id(model_id=model_id)
                == model_name
            )
        with pytest.raises(InstrumentModelNotRecognizedException):
            NGIIlluminaSequencingPlatform.model_name_from_id(
                model_id="non-existing-model"
            )
