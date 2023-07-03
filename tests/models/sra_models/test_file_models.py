import os
import pytest

from snpseq_metadata.exceptions import (
    ChecksumMethodNotRecognizedException,
    FiletypeNotRecognizedException,
)
from snpseq_metadata.models.sra_models import SRAResultFile


class TestSRAResultFile:
    def test_to_json(self, sra_result_file_obj, sra_result_file_json):
        assert sra_result_file_obj.to_json() == sra_result_file_json

    def test_from_json(self, sra_result_file_obj, sra_result_file_json):
        result_file = SRAResultFile.from_json(json_obj=sra_result_file_json)
        assert result_file == sra_result_file_obj.model_object

    def test_to_xml(self, sra_result_file_obj, sra_result_file_xml):
        assert sra_result_file_obj.to_xml(xml_declaration=False).split() == \
               sra_result_file_xml.split()

    def test_to_manifest(self, sra_result_file_obj, sra_result_file_manifest):
        assert sra_result_file_obj.to_manifest() == sra_result_file_manifest

    def test___getattr__(self, sra_result_file_obj, sra_result_file_json):
        assert sra_result_file_obj.filename == sra_result_file_json["filename"]
        assert sra_result_file_obj.checksum == sra_result_file_json["checksum"]
        assert sra_result_file_obj.filetype == sra_result_file_json["filetype"]
        assert sra_result_file_obj.checksum_method == sra_result_file_json["checksum_method"]

    def test___eq__(self, sra_result_file_obj, sra_result_file_json):
        def _check_match(variation, should_match=True):
            other_json = {
                k.replace("filename", "filepath"): v
                for k, v in sra_result_file_json.items()
            }
            other_json.update(variation)
            other_obj = SRAResultFile.create_object(**other_json)
            assert (other_obj == sra_result_file_obj) is should_match

        _check_match(
            {"filepath": os.path.join("/this", "is", "..", "is", "a", "file.path")}
        )

        variations = {
            "filepath": os.path.join("/this", "is", "another", "file.path"),
            "filetype": "bam",
            "checksum_method": "sha-256",
            "checksum": "this-does-not-match",
        }
        for k, v in variations.items():
            _check_match(
                {k: v},
                should_match=False,
            )

    def test_object_from_method(self, sra_result_file_obj, sra_result_file_json):
        assert (
            SRAResultFile.object_from_method(
                checksum_method=sra_result_file_json["checksum_method"]
            ).value
            == sra_result_file_obj.checksum_method
        )
        with pytest.raises(ChecksumMethodNotRecognizedException):
            SRAResultFile.object_from_method(
                checksum_method="non-existing-checksum-method"
            )

    def test_object_from_filetype(self, sra_result_file_obj, sra_result_file_json):
        assert (
            SRAResultFile.object_from_filetype(
                filetype=sra_result_file_json["filetype"]
            ).value
            == sra_result_file_obj.filetype
        )
        with pytest.raises(FiletypeNotRecognizedException):
            SRAResultFile.object_from_filetype(filetype="non-existing-filetype")

    def test_create_object(self, sra_result_file_obj, sra_result_file_json):
        result_file = SRAResultFile.create_object(
            **{
                k.replace("filename", "filepath"): v
                for k, v in sra_result_file_json.items()
            }
        )
        assert result_file == sra_result_file_obj
