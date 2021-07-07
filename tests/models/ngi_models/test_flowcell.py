import os
import pytest
import uuid

import snpseq_metadata.utilities
from snpseq_metadata.exceptions import FastqFileLocationNotFoundException
from snpseq_metadata.models.ngi_models import (
    NGIFlowcell,
    NGIIlluminaSequencingPlatform,
    NGIRun,
    NGIFastqFile,
)


class TestNGIFlowcell:
    def test_from_json(self, flowcell_obj, flowcell_json):
        flowcell = NGIFlowcell.from_json(json_obj=flowcell_json)
        assert flowcell == flowcell_obj

    def test_to_json(self, flowcell_obj, flowcell_json):
        obs_json = flowcell_obj.to_json()
        assert {k: obs_json.get(k) for k in flowcell_json.keys()} == flowcell_json

    def test_get_run_date(self, flowcell_obj, run_date):
        flowcell_obj.runfolder_name = f"{run_date.strftime('%y%m%d')}_whatever..."
        assert flowcell_obj.get_run_date() == run_date

        flowcell_obj.runfolder_name = f"{run_date.strftime('%Y%m%d')}_whatever..."
        assert flowcell_obj.get_run_date() == run_date

        flowcell_obj.runfolder_name = "this-can-not-be-parsed-as-a-date"
        assert flowcell_obj.get_run_date() is None

    def test_get_sequencing_platform(self, flowcell_obj, model_prefixes):
        (model_id, model_name) = model_prefixes.popitem()
        flowcell_obj.runfolder_name = f"datestring_{model_id}_whatever..."
        platform = flowcell_obj.get_sequencing_platform()
        assert isinstance(platform, NGIIlluminaSequencingPlatform)
        assert platform.model_name == model_name

    def test_get_checksumfile(self, flowcell_obj, monkeypatch):
        assert flowcell_obj.get_checksumfile() is None
        monkeypatch.setattr(os.path, "exists", lambda x: True)
        exp_checksum_file = os.path.join(
            flowcell_obj.runfolder_path, flowcell_obj.checksum_method, "checksums.md5"
        )
        assert flowcell_obj.get_checksumfile() == exp_checksum_file

    def test_get_sequencing_run_for_experiment(
        self, flowcell_obj, experiment_obj, run_obj
    ):
        obs_run_obj = flowcell_obj.get_sequencing_run_for_experiment(
            experiment=experiment_obj
        )
        assert obs_run_obj == run_obj

        flowcell_obj.sequencing_runs = []
        assert (
            flowcell_obj.get_sequencing_run_for_experiment(experiment=experiment_obj)
            is None
        )

    def test_get_sequencing_run_for_experiment_ref(
        self, flowcell_obj, experiment_ref_obj, fastq_file_obj, monkeypatch
    ):
        def fastqfiles(**kwargs):
            return [fastq_file_obj, fastq_file_obj]

        exp_run_obj = NGIRun(
            run_alias=f"{experiment_ref_obj.project.project_id}-{experiment_ref_obj.sample.sample_id}-{flowcell_obj.flowcell_id}",
            experiment=experiment_ref_obj,
            platform=flowcell_obj.platform,
            run_date=flowcell_obj.run_date,
            fastqfiles=fastqfiles(),
        )

        monkeypatch.setattr(
            flowcell_obj,
            "get_files_for_experiment_ref",
            fastqfiles,
        )
        obs_run_obj = flowcell_obj.get_sequencing_run_for_experiment_ref(
            experiment_ref=experiment_ref_obj
        )
        assert obs_run_obj == exp_run_obj

    def test_get_fastqdir_for_experiment_ref(
        self, flowcell_obj, experiment_ref_obj, tmpdir
    ):
        def _fastqdir_helper(l1, l2, l3, should_fail=False):
            runfolder = os.path.join(tmpdir, str(uuid.uuid4()))
            flowcell_obj.runfolder_path = runfolder
            fastqdir = os.path.join(runfolder, l1, l2, l3)
            os.makedirs(fastqdir)
            if should_fail:
                with pytest.raises(FastqFileLocationNotFoundException):
                    flowcell_obj.get_fastqdir_for_experiment_ref(experiment_ref_obj)
            else:
                assert (
                    flowcell_obj.get_fastqdir_for_experiment_ref(experiment_ref_obj)
                    == fastqdir
                )

        project_id = experiment_ref_obj.project.project_id
        sample_id = experiment_ref_obj.sample.sample_id
        for level_1 in ["Unaligned", "Demultiplexing"]:
            for level_2 in [project_id, f"Project_{project_id}"]:
                for level_3 in [sample_id, f"Sample_{sample_id}"]:
                    _fastqdir_helper(l1=level_1, l2=level_2, l3=level_3)
                _fastqdir_helper(
                    l1=level_1, l2=level_2, l3="not-recognized", should_fail=True
                )
            _fastqdir_helper(
                l1=level_1, l2="not-recognized", l3=sample_id, should_fail=True
            )
        _fastqdir_helper(
            l1="not-recognized", l2=project_id, l3=sample_id, should_fail=True
        )

    def test_get_files_for_experiment_ref(
        self, flowcell_obj, experiment_ref_obj, tmpdir, monkeypatch
    ):
        def _fastqdir(*args, **kwargs):
            return os.path.join(tmpdir, "fastq")

        def _checksum(checksumfile, querypath):
            return querypath

        # set up the test
        monkeypatch.setattr(flowcell_obj, "get_fastqdir_for_experiment_ref", _fastqdir)
        monkeypatch.setattr(
            snpseq_metadata.utilities, "lookup_checksum_from_file", _checksum
        )
        flowcell_obj.runfolder_path = tmpdir

        # define and touch files expected to be found and not to be found
        exp_fastqfiles = [
            os.path.join(_fastqdir(), fqfile)
            for fqfile in [
                "a-file.fastq",
                "b-file.fastq.gz",
                "c-file.fq",
                "d-file.fq.gz",
            ]
        ]
        nonexp_files = [
            os.path.join(_fastqdir(), nonfqfile)
            for nonfqfile in [
                "e-file.fasta",
                "f-file.fasta.gz",
                "g-file.fastq.zip",
                "h-file.fastq.gz.",
            ]
        ]
        os.makedirs(_fastqdir())
        for f in exp_fastqfiles + nonexp_files:
            open(f, "w").close()

        # sort the lists before comparison
        exp_objs = sorted(
            [
                NGIFastqFile(
                    filepath=fqfile,
                    checksum=os.path.join(
                        os.path.basename(tmpdir), "fastq", os.path.basename(fqfile)
                    ),
                    checksum_method=flowcell_obj.checksum_method,
                )
                for fqfile in exp_fastqfiles
            ],
            key=lambda x: x.filepath,
        )
        obs_objs = sorted(
            flowcell_obj.get_files_for_experiment_ref(
                experiment_ref=experiment_ref_obj
            ),
            key=lambda x: x.filepath,
        )
        assert obs_objs == exp_objs

    def test_get_experiments(
        self, flowcell_obj, samplesheet_rows, samplesheet_experiment_refs, monkeypatch
    ):
        def _samplesheet_rows(*args, **kwargs):
            return samplesheet_rows

        def _samplesheet_duplicate_rows(*args, **kwargs):
            return samplesheet_rows + samplesheet_rows

        monkeypatch.setattr(
            snpseq_metadata.utilities, "parse_samplesheet_data", _samplesheet_rows
        )
        assert flowcell_obj.get_experiments() == samplesheet_experiment_refs

        # assert that only unique experiments are returned
        monkeypatch.setattr(
            snpseq_metadata.utilities,
            "parse_samplesheet_data",
            _samplesheet_duplicate_rows,
        )
        assert flowcell_obj.get_experiments() == samplesheet_experiment_refs

        # assert that experiments can be restricted by project
        project_id = samplesheet_rows[0]["sample_project"]
        exp_experiments = list(
            filter(
                lambda x: x.project.project_id == project_id,
                samplesheet_experiment_refs,
            )
        )
        flowcell_obj.project_id = project_id
        assert flowcell_obj.get_experiments() == exp_experiments

        # assert that experiments can be restricted by sample
        sample_id = samplesheet_rows[0]["sample_id"]
        exp_experiments = list(
            filter(lambda x: x.sample.sample_id == sample_id, exp_experiments)
        )
        flowcell_obj.sample_id = sample_id
        assert flowcell_obj.get_experiments() == exp_experiments
