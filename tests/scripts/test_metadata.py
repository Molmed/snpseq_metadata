import os
import pathlib
import tempfile

from click.testing import CliRunner
from snpseq_metadata.scripts import metadata


def metadata_helper(*args):
    runner = CliRunner()
    result = runner.invoke(
        *args
    )
    assert result.exit_code == 0


class TestExportMetadata:

    def _export_helper(
        self,
        runfolder_ngi_json_file,
        experiment_set_ngi_json_file,
        export_mode,
    ):
        with tempfile.TemporaryDirectory(prefix="test_metadata_") as outdir:
            metadata_helper(
                metadata.metadata,
                [
                    "export",
                    "-o",
                    outdir,
                    runfolder_ngi_json_file,
                    experiment_set_ngi_json_file,
                    export_mode,
                ]
            )

    def test_export_tsv(
        self,
        runfolder_ngi_json_file,
        experiment_set_ngi_json_file,
    ):
        self._export_helper(
            runfolder_ngi_json_file,
            experiment_set_ngi_json_file,
            "tsv",
        )

    def test_export_manifest(
        self,
        runfolder_ngi_json_file,
        experiment_set_ngi_json_file,
    ):
        self._export_helper(
            runfolder_ngi_json_file,
            experiment_set_ngi_json_file,
            "manifest",
        )

    def test_export_xml(
        self,
        runfolder_ngi_json_file,
        experiment_set_ngi_json_file,
    ):
        self._export_helper(
            runfolder_ngi_json_file,
            experiment_set_ngi_json_file,
            "xml",
        )

    def test_export_json(
        self,
        runfolder_ngi_json_file,
        experiment_set_ngi_json_file,
    ):
        self._export_helper(
            runfolder_ngi_json_file,
            experiment_set_ngi_json_file,
            "json",
        )


class TestExtract:

    def _extract_helper(
            self,
            extract_type,
            input_obj,
    ):
        with tempfile.TemporaryDirectory(prefix="test_metadata_") as outdir:
            metadata_helper(
                metadata.metadata,
                [
                    "extract",
                    extract_type,
                    "-o",
                    outdir,
                    input_obj,
                    "json",
                ]
            )

    def test_extract_snpseq_data(
        self,
        experiment_set_lims_json_file,
    ):
        self._extract_helper(
            "snpseq-data",
            experiment_set_lims_json_file,
        )

    def test_extract_runfolder(
        self,
        runfolder_path,
    ):
        self._extract_helper(
            "runfolder",
            runfolder_path,
        )
