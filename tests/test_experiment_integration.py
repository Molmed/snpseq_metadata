import pytest

from snpseq_metadata.models.lims_models import LIMSSequencingContainer
from snpseq_metadata.models.ngi_models import NGIExperimentSet
from snpseq_metadata.models.sra_models import SRAExperimentSet
from snpseq_metadata.models.converter import Converter, ConvertExperimentSet

from tests.models.conftest import ignore_xml_namespace_attributes


@pytest.fixture
def lims_experiment_set_from_disk(experiment_set_lims_json):
    return LIMSSequencingContainer.from_json(json_obj=experiment_set_lims_json)


@pytest.fixture
def ngi_experiment_set_from_lims_sequencing_container(lims_experiment_set_from_disk):
    return ConvertExperimentSet.lims_to_ngi(lims_model=lims_experiment_set_from_disk)


@pytest.fixture
def ngi_experiment_set_from_json(experiment_set_ngi_json):
    return NGIExperimentSet.from_json(json_obj=experiment_set_ngi_json)


@pytest.fixture
def sra_experiment_set_from_ngi(ngi_experiment_set_from_json):
    return Converter.ngi_to_sra(ngi_model=ngi_experiment_set_from_json)


@pytest.fixture
def sra_experiment_set_manifest(
    sra_experiment_set_from_ngi, experiment_set_sra_json_file
):
    def _parse_manifest(_manifest_file):
        with open(_manifest_file) as fh:
            return [tuple(line.strip().split("\t")) for line in fh]

    manifest = []
    for experiment in sra_experiment_set_from_ngi.experiments:
        manifest_file = f'{".".join(experiment_set_sra_json_file.split(".")[0:-2])}.{experiment.model_object.alias}.sra.manifest'
        manifest.extend(_parse_manifest(manifest_file))
    return manifest


class TestLIMSSequencingContainer:
    def test_lims_experiment_set_from_json(
        self, lims_experiment_set_from_disk, experiment_set_name, experiment_set_samples
    ):
        # create a samples dict with sample names as keys
        samples_dict = {sample["name"]: sample for sample in experiment_set_samples}
        assert type(lims_experiment_set_from_disk) is LIMSSequencingContainer
        assert lims_experiment_set_from_disk.name == experiment_set_name
        assert len(lims_experiment_set_from_disk.samples) == len(experiment_set_samples)
        for lims_experiment_set_sample in lims_experiment_set_from_disk.samples:
            sample_id = lims_experiment_set_sample.sample_id
            assert sample_id in samples_dict
            assert (
                lims_experiment_set_sample.project_id
                == samples_dict[sample_id]["project"]
            )
            for udf_name in samples_dict[sample_id].keys():
                if udf_name not in ["project", "name"]:
                    assert (
                        getattr(lims_experiment_set_sample, udf_name)
                        == samples_dict[sample_id][udf_name]
                    )

    def test_lims_experiment_set_to_json(
        self, lims_experiment_set_from_disk, experiment_set_lims_json
    ):
        assert lims_experiment_set_from_disk.to_json() == experiment_set_lims_json


class TestNGIExperimentSet:
    def test_convert_sequencing_container_to_experiment_set(
        self, ngi_experiment_set_from_lims_sequencing_container
    ):
        assert (
            type(ngi_experiment_set_from_lims_sequencing_container) is NGIExperimentSet
        )

    def test_to_json(
        self, ngi_experiment_set_from_lims_sequencing_container, experiment_set_ngi_json
    ):
        assert (
            ngi_experiment_set_from_lims_sequencing_container.to_json()
            == experiment_set_ngi_json
        )

    def test_from_json(
        self,
        ngi_experiment_set_from_json,
        ngi_experiment_set_from_lims_sequencing_container,
    ):
        assert (
            ngi_experiment_set_from_json
            == ngi_experiment_set_from_lims_sequencing_container
        )


class TestSRAExperimentSet:
    def test_convert_ngi_to_sra(self, sra_experiment_set_from_ngi):
        assert type(sra_experiment_set_from_ngi) is SRAExperimentSet

    def test_to_json(self, sra_experiment_set_from_ngi, experiment_set_sra_json):
        assert sra_experiment_set_from_ngi.to_json() == experiment_set_sra_json

    def test_to_xml(self, sra_experiment_set_from_ngi, experiment_set_sra_xml):
        observed_xml = ignore_xml_namespace_attributes(sra_experiment_set_from_ngi.to_xml())
        assert observed_xml == experiment_set_sra_xml

    def test_to_manifest(
        self, sra_experiment_set_from_ngi, sra_experiment_set_manifest
    ):
        assert sra_experiment_set_from_ngi.to_manifest() == sra_experiment_set_manifest
