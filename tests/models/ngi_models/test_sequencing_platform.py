import pytest

from snpseq_metadata.exceptions import InstrumentModelNotRecognizedException
from snpseq_metadata.models.ngi_models import (
    NGISequencingPlatform,
    NGIIlluminaSequencingPlatform,
)


class TestNGISequencingPlatform:
    def test_from_json(self, ngi_platform_obj, ngi_platform_json):
        platform = NGISequencingPlatform.from_json(json_obj=ngi_platform_json)
        assert platform == ngi_platform_obj

    def test_to_json(self, ngi_platform_obj, ngi_platform_json):
        assert ngi_platform_obj.to_json() == ngi_platform_json

    def test_model_name_parsing(self, illumina_model_names):
        for inp_name, model_name in illumina_model_names.items():
            if model_name is not None:
                model = NGIIlluminaSequencingPlatform(model_name=inp_name)
                assert model.model_name == model_name
            else:
                with pytest.raises(InstrumentModelNotRecognizedException):
                    NGIIlluminaSequencingPlatform(model_name=inp_name)


class TestNGIIlluminaSequencingPlatform:
    def test_model_name_from_id(self, illumina_model_prefixes):
        for model_id, model_name in illumina_model_prefixes.items():
            assert (
                NGIIlluminaSequencingPlatform.model_name_from_id(model_id=model_id)
                == model_name
            )
        with pytest.raises(InstrumentModelNotRecognizedException):
            NGIIlluminaSequencingPlatform.model_name_from_id(
                model_id="non-existing-model"
            )
