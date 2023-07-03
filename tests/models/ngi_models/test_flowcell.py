import os
import pytest
import uuid

import snpseq_metadata.utilities
from snpseq_metadata.exceptions import FastqFileLocationNotFoundException
from snpseq_metadata.models.ngi_models import (
    NGIAttribute,
    NGIFlowcell,
    NGIIlluminaSequencingPlatform,
    NGIRun,
    NGIFastqFile,
)


class TestNGIFlowcell:
    def test_from_json(self, ngi_flowcell_obj, ngi_flowcell_json):
        flowcell = NGIFlowcell.from_json(json_obj=ngi_flowcell_json)
        assert flowcell == ngi_flowcell_obj

    def test_to_json(self, ngi_flowcell_obj, ngi_flowcell_json):
        obs_json = ngi_flowcell_obj.to_json()
        assert {
            k: obs_json.get(k) for k in ngi_flowcell_json.keys()
        } == ngi_flowcell_json

    def test_get_run_date(self, ngi_flowcell_obj, run_date):
        ngi_flowcell_obj.runfolder_name = f"{run_date.strftime('%y%m%d')}_whatever..."
        assert ngi_flowcell_obj.get_run_date() == run_date

        ngi_flowcell_obj.runfolder_name = f"{run_date.strftime('%Y%m%d')}_whatever..."
        assert ngi_flowcell_obj.get_run_date() == run_date

        ngi_flowcell_obj.runfolder_name = "this-can-not-be-parsed-as-a-date"
        assert ngi_flowcell_obj.get_run_date() is None

    def test_get_flowcell_id_from_runfolder_name(self, run_date, flowcell_id):
        date_formats = [
            run_date.strftime("%y%m%d"),
            run_date.strftime("%Y%m%d")
        ]
        instrument_ids = ["A0123", "FS000012", "M00145"]
        flowcell_positions = ["A", "X", ""]
        flowcell_ids = [flowcell_id, flowcell_id, f"00000-{flowcell_id}"]

        runfolder_names = []
        expected_fcids = []
        for date_str in date_formats:
            for instrument_id in instrument_ids:
                for flowcell_position, fcid in zip(flowcell_positions, flowcell_ids):
                    runfolder_names.append(
                        "_".join([
                            date_str,
                            instrument_id,
                            "0123",
                            f"{flowcell_position}{fcid}"
                        ])
                    )
                    expected_fcids.append(fcid)

        for runfolder_name, expected_fcid in zip(runfolder_names, expected_fcids):
            obs_fcid = NGIFlowcell.get_flowcell_id_from_runfolder_name(runfolder_name)
            assert obs_fcid == expected_fcid

    def test_get_sequencing_platform(self, ngi_flowcell_obj, illumina_model_prefixes):
        (model_id, model_name) = illumina_model_prefixes.popitem()
        ngi_flowcell_obj.runfolder_name = f"datestring_{model_id}_whatever..."
        platform = ngi_flowcell_obj.get_sequencing_platform()
        assert isinstance(platform, NGIIlluminaSequencingPlatform)
        assert platform.model_name == model_name

    def test_get_checksumfile(self, ngi_flowcell_obj, monkeypatch):
        assert ngi_flowcell_obj.get_checksumfile() is None
        monkeypatch.setattr(os.path, "exists", lambda x: True)
        exp_checksum_file = os.path.join(
            ngi_flowcell_obj.runfolder_path,
            ngi_flowcell_obj.checksum_method,
            "checksums.md5",
        )
        assert ngi_flowcell_obj.get_checksumfile() == exp_checksum_file

    def test_get_sequencing_run_for_experiment(
        self, ngi_flowcell_obj, ngi_experiment_obj, ngi_sequencing_run_obj
    ):
        obs_run_obj = ngi_flowcell_obj.get_sequencing_run_for_experiment(
            experiment=ngi_experiment_obj
        )
        assert obs_run_obj == ngi_sequencing_run_obj

        ngi_flowcell_obj.sequencing_runs = []
        assert (
            ngi_flowcell_obj.get_sequencing_run_for_experiment(
                experiment=ngi_experiment_obj
            )
            is None
        )

    def test_get_sequencing_run_for_experiment_ref(
            self,
            ngi_flowcell_obj,
            ngi_experiment_ref_obj,
            ngi_fastq_file_obj,
            ngi_study_obj,
            ngi_sample_obj,
            monkeypatch):

        def fastqfiles(**kwargs):
            return [ngi_fastq_file_obj, ngi_fastq_file_obj]

        exp_run_obj = NGIRun(
            run_alias=f"{ngi_experiment_ref_obj.alias}-{ngi_flowcell_obj.flowcell_id}",
            experiment=ngi_experiment_ref_obj,
            platform=ngi_flowcell_obj.platform,
            run_date=ngi_flowcell_obj.run_date,
            fastqfiles=fastqfiles(),
            run_attributes=[
                NGIAttribute(tag="project_id", value=ngi_study_obj.project_id),
                NGIAttribute(tag="sample_id", value=ngi_sample_obj.sample_id)
            ]
        )

        monkeypatch.setattr(
            ngi_flowcell_obj,
            "get_files_for_experiment_ref",
            fastqfiles,
        )
        obs_run_obj = ngi_flowcell_obj.get_sequencing_run_for_experiment_ref(
            experiment_ref=ngi_experiment_ref_obj
        )
        assert obs_run_obj == exp_run_obj

    def test_get_fastqdir_for_experiment_ref(
        self, ngi_flowcell_obj, ngi_experiment_ref_obj, tmpdir
    ):
        def _fastqdir_helper(l1, l2, l3, should_fail=False):
            runfolder = os.path.join(tmpdir, str(uuid.uuid4()))
            ngi_flowcell_obj.runfolder_path = runfolder
            fastqdir = os.path.join(runfolder, l1, l2, l3)
            os.makedirs(fastqdir)
            if should_fail:
                with pytest.raises(FastqFileLocationNotFoundException):
                    ngi_flowcell_obj.get_fastqdir_for_experiment_ref(
                        ngi_experiment_ref_obj
                    )
            else:
                assert (
                    ngi_flowcell_obj.get_fastqdir_for_experiment_ref(
                        ngi_experiment_ref_obj
                    )
                    == fastqdir
                )

        project_id = ngi_experiment_ref_obj.project.project_id
        sample_id = ngi_experiment_ref_obj.sample.sample_id
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
        self, ngi_flowcell_obj, ngi_experiment_ref_obj, tmpdir, monkeypatch
    ):
        def _fastqdir(*args, **kwargs):
            return os.path.join(tmpdir, "fastq")

        def _checksum(queryfile, method):
            return f"{method}-{os.path.basename(queryfile)}"

        # set up the test
        monkeypatch.setattr(
            ngi_flowcell_obj, "get_fastqdir_for_experiment_ref", _fastqdir
        )
        monkeypatch.setattr(
            snpseq_metadata.utilities, "calculate_checksum_from_file", _checksum
        )
        ngi_flowcell_obj.runfolder_path = tmpdir

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
                    checksum=f"{ngi_flowcell_obj.checksum_method}-{os.path.basename(fqfile)}",
                    checksum_method=ngi_flowcell_obj.checksum_method,
                )
                for fqfile in exp_fastqfiles
            ],
            key=lambda x: x.filepath,
        )
        obs_objs = sorted(
            ngi_flowcell_obj.get_files_for_experiment_ref(
                experiment_ref=ngi_experiment_ref_obj
            ),
            key=lambda x: x.filepath,
        )
        assert obs_objs == exp_objs

    def test_get_experiments(
        self,
        ngi_flowcell_obj,
        samplesheet_rows,
        samplesheet_experiment_refs,
        monkeypatch,
    ):
        def _samplesheet_rows(*args, **kwargs):
            return samplesheet_rows

        def _samplesheet_duplicate_rows(*args, **kwargs):
            return samplesheet_rows + samplesheet_rows

        monkeypatch.setattr(
            snpseq_metadata.utilities, "parse_samplesheet_data", _samplesheet_rows
        )
        assert ngi_flowcell_obj.get_experiments() == samplesheet_experiment_refs

        # assert that only unique experiments are returned
        monkeypatch.setattr(
            snpseq_metadata.utilities,
            "parse_samplesheet_data",
            _samplesheet_duplicate_rows,
        )
        assert ngi_flowcell_obj.get_experiments() == samplesheet_experiment_refs

        # assert that experiments can be restricted by project
        project_id = samplesheet_rows[0]["sample_project"]
        exp_experiments = list(
            filter(
                lambda x: x.project.project_id == project_id,
                samplesheet_experiment_refs,
            )
        )
        ngi_flowcell_obj.project_id = project_id
        assert ngi_flowcell_obj.get_experiments() == exp_experiments

        # assert that experiments can be restricted by sample
        sample_id = samplesheet_rows[0]["sample_id"]
        exp_experiments = list(
            filter(lambda x: x.sample.sample_id == sample_id, exp_experiments)
        )
        ngi_flowcell_obj.sample_id = sample_id
        assert ngi_flowcell_obj.get_experiments() == exp_experiments
