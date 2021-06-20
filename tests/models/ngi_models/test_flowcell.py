import os

import snpseq_metadata.utilities


class TestFlowcell:
    @staticmethod
    def _return_none(*args):
        return None

    @staticmethod
    def _return_true(*args):
        return True

    @staticmethod
    def _return_samplesheet(*args):
        return ["this-is-a-samplesheet"]

    @staticmethod
    def _return_alt_samplesheet(*args):
        return ["this-is-another-samplesheet"]

    @staticmethod
    def _return_samplesheet_data(*args):
        required_fields = ["sample_project", "sample_id"]
        additional_fields = [f"field_{i}" for i in range(3)]
        samplesheet_data = []
        for i in range(5):
            for j in range(2):
                samplesheet_data.append(
                    dict(zip(required_fields, [f"project_{i}{j}", f"sample_{i}{j}"]))
                )
                samplesheet_data[-1]["description"] = f"some-data:experiment-name-{i}"
                samplesheet_data[-1].update(
                    {k: f"{k}_{i}{j}" for k in additional_fields}
                )
        return samplesheet_data

    @staticmethod
    def _return_os_listdir(dir, *args):
        return_values = {
            "Unaligned": [
                "a-directory",
                "AnotherProject",
                "Project_SampleProject",
            ],
            "Project_SampleProject": [
                "a-directory",
                "Sample_AnotherSampleID",
                "SampleID",
            ],
            "AnotherProject": ["a-directory", "Sample_AnotherSampleID", "SampleID"],
        }
        return return_values.get(os.path.basename(dir), ["some-directory", "Unaligned"])

    def test_get_experiments(self, monkeypatch):
        monkeypatch.setattr(
            snpseq_metadata.utilities,
            "parse_samplesheet_data",
            self._return_samplesheet_data,
        )
        monkeypatch.setattr(Flowcell, "get_run_set", self._return_none)

        runfolder_name = "this-is-a-runfolder-name"
        runfolder_path = os.path.join(
            "/this", "is", "a", "runfolder", "path", runfolder_name
        )
        samplesheet_name = "this-is-a-supplied-samplesheet"
        run_parameters_name = "this-is-a-supplied-run_parameters"

        fc = Flowcell(
            runfolder_path=runfolder_path,
            samplesheet=samplesheet_name,
            run_parameters=run_parameters_name,
        )
        experiments = fc.get_experiments()

        samplesheet_data = self._return_samplesheet_data()
        experiment_names = list(
            set([row["description"].split(":")[-1] for row in samplesheet_data])
        )
        assert sorted(
            [experiment.experiment_name for experiment in experiments]
        ) == sorted(experiment_names)

    def test_get_checksumfile(self, monkeypatch):
        runfolder_path = os.path.join(".", "resources")
        monkeypatch.setattr(Flowcell, "get_run_set", self._return_none)
        fc = Flowcell(
            runfolder_path=runfolder_path,
            samplesheet="this-is-a-samplesheet",
            run_parameters="this-is-run-parameters",
        )
        assert fc.get_checksumfile() == os.path.join(
            runfolder_path, "MD5", "checksums.md5"
        )

    def test_get_fastqdir_for_experiment(self, monkeypatch):
        runfolder_name = "this-is-a-runfolder-name"
        runfolder_path = os.path.join(
            "/this", "is", "a", "runfolder", "path", runfolder_name
        )
        samplesheet_name = "this-is-a-supplied-samplesheet"
        run_parameters_name = "this-is-a-supplied-run_parameters"
        monkeypatch.setattr(Flowcell, "get_run_set", self._return_none)

        fc = Flowcell(
            runfolder_path=runfolder_path,
            samplesheet=samplesheet_name,
            run_parameters=run_parameters_name,
        )
        monkeypatch.setattr(os.path, "isdir", self._return_true)
        monkeypatch.setattr(os, "listdir", self._return_os_listdir)

        experiment_ref = ExperimentRef(
            experiment_name="this-is-an-experiment-name",
            sample_project="SampleProject",
            sample_id="SampleID",
        )
        fastq_dir = fc.get_fastqdir_for_experiment(experiment=experiment_ref)
        assert fastq_dir == os.path.join(
            runfolder_path,
            "Unaligned",
            f"Project_{experiment_ref.sample_project}",
            experiment_ref.sample_id,
        )

        experiment_ref = ExperimentRef(
            experiment_name="this-is-another-experiment-name",
            sample_project="AnotherProject",
            sample_id="AnotherSampleID",
        )
        fastq_dir = fc.get_fastqdir_for_experiment(experiment=experiment_ref)
        assert fastq_dir == os.path.join(
            runfolder_path,
            "Unaligned",
            experiment_ref.sample_project,
            f"Sample_{experiment_ref.sample_id}",
        )

    def test_integration(self):
        runfolder_path = os.path.join(".", "resources", "210415_A00001_0123_BXYZ321XY")
        fc = Flowcell(runfolder_path=runfolder_path)
        print(fc.to_xml())
