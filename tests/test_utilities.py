import os
import pytest

from snpseq_metadata.exceptions import SampleSheetNotFoundException
import snpseq_metadata.utilities


def test_calculate_checksum_from_file(file_checksums):
    for testfile, checksum in file_checksums.items():
        assert (
            snpseq_metadata.utilities.calculate_checksum_from_file(
                queryfile=testfile, method=testfile.split(".")[-1].upper()
            )
            == checksum
        )


def test_parse_samplesheet_data(samplesheet_file, samplesheet_data):
    assert (
        snpseq_metadata.utilities.parse_samplesheet_data(samplesheet_file)
        == samplesheet_data
    )


def test_find_samplesheet(monkeypatch):
    def _listdir_no_samplesheet(*args):
        return ["file1", "file2", "file3"]

    def _listdir_one_samplesheet(*args):
        return ["file1", "file2_SampleSheet.csv", "file3"]

    def _listdir_two_samplesheet(*args):
        return ["file1", "samplesheet.csv", "file2_SampleSheet.csv"]

    runfolder = os.path.join("this", "is", "a", "runfolder")

    # assert that finding no samplesheet raises an exception
    monkeypatch.setattr(os, "listdir", _listdir_no_samplesheet)
    with pytest.raises(SampleSheetNotFoundException):
        snpseq_metadata.utilities.find_samplesheet(runfolder)

    # assert that the expected samplesheet can be found
    monkeypatch.setattr(os, "listdir", _listdir_one_samplesheet)
    assert snpseq_metadata.utilities.find_samplesheet(runfolder) == [
        _listdir_one_samplesheet()[1]
    ]

    # assert that all samplesheets are returned when multiple are present
    monkeypatch.setattr(os, "listdir", _listdir_two_samplesheet)
    assert (
        snpseq_metadata.utilities.find_samplesheet(runfolder)
        == _listdir_two_samplesheet()[1:]
    )

    # assert that a supplied suffix is used
    assert snpseq_metadata.utilities.find_samplesheet(runfolder, suffix="e1") == [
        _listdir_two_samplesheet()[0]
    ]


def test_find_existing_samplesheet(test_resources_path, samplesheet_file):
    # assert that an existing samplesheet can be found on disk
    assert snpseq_metadata.utilities.find_samplesheet(test_resources_path) == [
        os.path.basename(samplesheet_file)
    ]


def test_lookup_checksum_from_file(test_resources_path, checksum_file, file_checksums):

    # if a checksum file is missing, the method will throw an exception
    with pytest.raises(OSError):
        snpseq_metadata.utilities.lookup_checksum_from_file(
            checksumfile="this-file-does-not-exist", querypath="does-not-matter"
        )

    # for files having checksums in a file, assert that they can be retrieved
    for testfile, expected_checksum in file_checksums.items():
        querypath = os.path.relpath(testfile, os.path.dirname(test_resources_path))
        assert (
            snpseq_metadata.utilities.lookup_checksum_from_file(
                checksumfile=checksum_file, querypath=querypath
            )
            == expected_checksum
        )
