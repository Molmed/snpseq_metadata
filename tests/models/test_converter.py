from snpseq_metadata.models.converter import *


class TestConvertSampleDescriptor:
    def test_ngi_to_sra(self, ngi_sample_obj, sra_sample_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_sample_obj) == sra_sample_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_sample_obj):
        assert (
            ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_sample_obj)
            == ngi_sample_obj
        )


class TestConvertStudyRef:
    def test_ngi_to_sra(self, ngi_study_obj, sra_study_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_study_obj) == sra_study_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_study_obj):
        assert ConvertStudyRef.lims_to_ngi(lims_model=lims_sample_obj) == ngi_study_obj


class TestConvertRun:
    def test_ngi_to_sra(self, ngi_sequencing_run_obj, sra_sequencing_run_obj):
        # the converter will just use a reference to the experiment so make sure that we have that
        # on the SRA object
        sra_sequencing_run_obj.experiment = (
            sra_sequencing_run_obj.experiment.get_reference()
        )
        obs = Converter.ngi_to_sra(ngi_model=ngi_sequencing_run_obj)
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_sequencing_run_obj)
            == sra_sequencing_run_obj
        )

    def test_lims_to_ngi(self, lims_sequencing_container_obj):
        assert ConvertRun.lims_to_ngi(lims_model=lims_sequencing_container_obj) is None


class TestConvertSequencingPlatform:
    def test_ngi_to_sra(self, ngi_illumina_platform_obj, sra_sequencing_platform_obj):
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_illumina_platform_obj)
            == sra_sequencing_platform_obj
        )

    def test_lims_to_ngi(self, lims_sample_obj, ngi_illumina_platform_obj):
        assert (
            ConvertSequencingPlatform.lims_to_ngi(lims_model=lims_sample_obj)
            == ngi_illumina_platform_obj
        )


class TestConvertRunSet:
    def test_ngi_to_sra(self, ngi_flowcell_obj, sra_sequencing_run_set_obj):
        # the converter will just use a reference to the experiment so make sure that we have that
        # on the SRA object
        for sequencing_run in sra_sequencing_run_set_obj.runs:
            sequencing_run.experiment = sequencing_run.experiment.get_reference()
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_flowcell_obj)
            == sra_sequencing_run_set_obj
        )

    def test_lims_to_ngi(self, lims_sample_obj):
        assert ConvertRunSet.lims_to_ngi(lims_model=lims_sample_obj) is None


class TestConvertResultFile:
    def test_ngi_to_sra(self, ngi_result_file_obj, sra_result_file_obj):
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_result_file_obj) == sra_result_file_obj
        )

    def test_lims_to_ngi(self, lims_sample_obj):
        assert ConvertResultFile.lims_to_ngi(lims_model=lims_sample_obj) is None


class TestConvertExperimentRef:
    def test_ngi_to_sra(self, ngi_experiment_ref_obj, sra_experiment_ref_obj):
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_experiment_ref_obj)
            == sra_experiment_ref_obj
        )

    def test_lims_to_ngi(self, lims_sample_obj, ngi_experiment_ref_obj):
        experiment_ref = ConvertExperimentRef.lims_to_ngi(lims_model=lims_sample_obj)
        # the converted object will have a derived alias that don't correspond to the fixture so
        # we'll adjust for that
        experiment_ref.alias = ngi_experiment_ref_obj.alias
        assert experiment_ref == ngi_experiment_ref_obj


class TestConvertExperimentSet:
    def test_ngi_to_sra(self, ngi_experiment_set_obj, sra_experiment_set_obj):
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_experiment_set_obj)
            == sra_experiment_set_obj
        )

    def test_lims_to_ngi(self, lims_sequencing_container_obj, ngi_experiment_set_obj):
        # the converted object will have a derived alias and title that don't correspond to the
        # fixture so we'll adjust for that
        experiment_set = ConvertExperimentSet.lims_to_ngi(
            lims_model=lims_sequencing_container_obj
        )
        for experiment, ngi_experiment_obj in zip(
            experiment_set.experiments, ngi_experiment_set_obj.experiments
        ):
            experiment.alias = ngi_experiment_obj.alias
            experiment.title = ngi_experiment_obj.title
            # same thing with the library description...
            experiment.library.description = ngi_experiment_obj.library.description
        assert experiment_set == ngi_experiment_set_obj


class TestConvertLibrary:
    def test_ngi_to_sra(self, ngi_library_obj, sra_library_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_library_obj) == sra_library_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_library_obj):
        # the converted object will have a derived description that don't correspond to the
        # fixture so we'll adjust for that
        library = ConvertLibrary.lims_to_ngi(lims_model=lims_sample_obj)
        library.description = ngi_library_obj.description
        assert library == ngi_library_obj

    def test_objects_from_application_info(self, test_values):
        assert ConvertLibrary.objects_from_application_info(
            application=test_values["library_application"],
            sample_type=test_values["library_sample_type"],
            library_kit=test_values["library_kit"],
        ) == (
            test_values["library_selection"],
            test_values["library_source"],
            test_values["library_strategy"],
        )


class TestConvertExperiment:
    def test_ngi_to_sra(self, ngi_experiment_obj, sra_experiment_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_experiment_obj) == sra_experiment_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_experiment_obj):
        # the converted object will have a derived alias and title that don't correspond to the
        # fixture so we'll adjust for that
        experiment = ConvertExperiment.lims_to_ngi(lims_model=lims_sample_obj)
        experiment.alias = ngi_experiment_obj.alias
        experiment.title = ngi_experiment_obj.title
        # same thing with the library description...
        experiment.library.description = ngi_experiment_obj.library.description
        assert experiment == ngi_experiment_obj
