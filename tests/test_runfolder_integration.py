import pytest

from snpseq_metadata.models.ngi_models import NGIFlowcell
from snpseq_metadata.models.sra_models import SRARunSet
from snpseq_metadata.models.converter import Converter


@pytest.fixture
def ngi_flowcell_from_disk(runfolder_path):
    return NGIFlowcell(runfolder_path=runfolder_path)


@pytest.fixture
def sra_run_set_from_ngi_flowcell(ngi_flowcell_from_disk):
    return Converter.ngi_to_sra(ngi_model=ngi_flowcell_from_disk)


class TestNGIFlowcell:
    def test_parse_flowcell_from_disk(
        self,
        ngi_flowcell_from_disk,
        runfolder_run_date,
        runfolder_flowcell_id,
        runfolder_samplesheet,
        runfolder_run_parameters,
    ):
        assert type(ngi_flowcell_from_disk) is NGIFlowcell
        assert ngi_flowcell_from_disk.run_date == runfolder_run_date
        assert ngi_flowcell_from_disk.flowcell_id == runfolder_flowcell_id
        assert ngi_flowcell_from_disk.samplesheet == runfolder_samplesheet
        assert ngi_flowcell_from_disk.run_parameters == runfolder_run_parameters

    def test_to_json(self, ngi_flowcell_from_disk, runfolder_ngi_json):
        assert ngi_flowcell_from_disk.to_json() == runfolder_ngi_json


class TestSRAFlowcell:
    def test_convert_flowcell_to_run_set(self, sra_run_set_from_ngi_flowcell):
        assert type(sra_run_set_from_ngi_flowcell) is SRARunSet

    def test_to_json(self, sra_run_set_from_ngi_flowcell, runfolder_sra_json):
        assert sra_run_set_from_ngi_flowcell.to_json() == runfolder_sra_json

    def test_to_xml(self, sra_run_set_from_ngi_flowcell, runfolder_sra_xml):
        assert "".join(sra_run_set_from_ngi_flowcell.to_xml().split()) == "".join(
            runfolder_sra_xml.split()
        )

    def test_to_manifest(self, sra_run_set_from_ngi_flowcell, runfolder_sra_manifest):
        assert sra_run_set_from_ngi_flowcell.to_manifest() == runfolder_sra_manifest
