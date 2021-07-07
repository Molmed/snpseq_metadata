import os
import pytest

from snpseq_metadata.exceptions import (
    ChecksumMethodNotRecognizedException,
    FiletypeNotRecognizedException,
)
from snpseq_metadata.models.sra_models import SRAResultFile


class TestSRAResultFile:
    def test_to_json(self, result_file_obj, result_file_json):
        assert result_file_obj.to_json() == result_file_json

    def test_from_json(self, result_file_obj, result_file_json):
        result_file = SRAResultFile.from_json(json_obj=result_file_json)
        assert result_file == result_file_obj.model_object

    def test_to_xml(self, result_file_obj, result_file_xml):
        assert result_file_xml in result_file_obj.to_xml()

    def test_to_manifest(self, result_file_obj, result_file_manifest):
        assert result_file_obj.to_manifest() == result_file_manifest

    def test___eq__(self, result_file_obj, result_file_json):
        def _check_match(variation, should_match=True):
            other_json = {
                k.replace("filename", "filepath"): v
                for k, v in result_file_json.items()
            }
            other_json.update(variation)
            other_obj = SRAResultFile.create_object(**other_json)
            assert (other_obj == result_file_obj) is should_match

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

    def test_object_from_method(self, result_file_obj, result_file_json):
        assert (
            SRAResultFile.object_from_method(
                checksum_method=result_file_json["checksum_method"]
            )
            == result_file_obj.model_object.checksum_method
        )
        with pytest.raises(ChecksumMethodNotRecognizedException):
            SRAResultFile.object_from_method(
                checksum_method="non-existing-checksum-method"
            )

    def test_object_from_filetype(self, result_file_obj, result_file_json):
        assert (
            SRAResultFile.object_from_filetype(filetype=result_file_json["filetype"])
            == result_file_obj.model_object.filetype
        )
        with pytest.raises(FiletypeNotRecognizedException):
            SRAResultFile.object_from_filetype(filetype="non-existing-filetype")

    def test_create_object(self, result_file_obj, result_file_json):
        result_file = SRAResultFile.create_object(
            **{
                k.replace("filename", "filepath"): v
                for k, v in result_file_json.items()
            }
        )
        assert result_file == result_file_obj
