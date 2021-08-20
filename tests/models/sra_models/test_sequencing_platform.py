import pytest

from snpseq_metadata.exceptions import InstrumentModelNotRecognizedException
from snpseq_metadata.models.xsdata.sra_common import TypeIlluminaModel
from snpseq_metadata.models.sra_models import SRAIlluminaSequencingPlatform


class TestSRAIlluminaSequencingPlatform:
    def test_from_json(self, sra_sequencing_platform_obj, sra_sequencing_platform_json):
        platform = SRAIlluminaSequencingPlatform.from_json(
            json_obj=sra_sequencing_platform_json
        )
        assert platform == sra_sequencing_platform_obj.model_object

    def test_to_json(self, sra_sequencing_platform_obj, sra_sequencing_platform_json):
        assert sra_sequencing_platform_obj.to_json() == sra_sequencing_platform_json

    def test_to_manifest(
        self, sra_sequencing_platform_obj, sra_sequencing_platform_manifest
    ):
        assert (
            sra_sequencing_platform_obj.to_manifest()
            == sra_sequencing_platform_manifest
        )

    def test_to_xml(self, sra_sequencing_platform_obj, sra_sequencing_platform_xml):
        assert "".join(sra_sequencing_platform_xml.split()) in "".join(
            sra_sequencing_platform_obj.to_xml().split()
        )

    def test_create_object(
        self,
        sra_sequencing_platform_obj,
        sra_sequencing_platform_json,
        illumina_sequencing_platforms,
    ):
        sequencing_platform = SRAIlluminaSequencingPlatform.create_object(
            model_name=illumina_sequencing_platforms[0]
        )
        assert sequencing_platform == sra_sequencing_platform_obj

    def test_object_from_name(self, illumina_sequencing_platforms):
        for model_name in illumina_sequencing_platforms + ["", None]:
            assert isinstance(
                SRAIlluminaSequencingPlatform.object_from_name(model_name=model_name),
                TypeIlluminaModel,
            )
        with pytest.raises(InstrumentModelNotRecognizedException):
            SRAIlluminaSequencingPlatform.object_from_name(
                model_name="this-is-not-recognized"
            )
