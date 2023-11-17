import pytest

from snpseq_metadata.models.converter import *


class TestConverter:

    # Failure to convert a model should raise the appropriate exception
    def test_ngi_to_sra_exception(self):
        with pytest.raises(SRAModelConversionException):
            assert Converter.ngi_to_sra(ngi_model=None)

    def test_lims_to_ngi_exception(self):
        with pytest.raises(NGIModelConversionException):
            assert Converter.lims_to_ngi(lims_model=None)


class TestConvertSampleDescriptor:
    def test_ngi_to_sra(self, ngi_sample_obj, sra_sample_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_sample_obj) == sra_sample_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_sample_obj):
        # the lims_sample_obj will not have enough information to deduce the sample_name
        ngi_sample_obj.sample_name = ngi_sample_obj.sample_id
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
        # we'll adjust for that. Likewise the sample.sample_name field
        experiment_ref.alias = ngi_experiment_ref_obj.alias
        experiment_ref.sample.sample_name = ngi_experiment_ref_obj.sample.sample_name
        assert experiment_ref == ngi_experiment_ref_obj


class TestConvertExperimentSet:
    def test_ngi_to_sra(self, ngi_experiment_set_obj, sra_experiment_set_obj):
        assert (
            Converter.ngi_to_sra(ngi_model=ngi_experiment_set_obj)
            == sra_experiment_set_obj
        )

    def test_lims_to_ngi(self, lims_sequencing_container_obj, ngi_experiment_set_obj):
        experiment_set = ConvertExperimentSet.lims_to_ngi(
            lims_model=lims_sequencing_container_obj
        )
        assert len(experiment_set.experiments) == len(ngi_experiment_set_obj.experiments)
        for experiment, ngi_experiment_obj in zip(
            experiment_set.experiments, ngi_experiment_set_obj.experiments
        ):
            assert type(experiment) == type(ngi_experiment_obj)


class TestConvertLibrary:
    def test_ngi_to_sra(self, ngi_library_obj, sra_library_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_library_obj) == sra_library_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_library_obj):
        # the converted object will have a derived description that don't correspond to the
        # fixture so only compare attributes that can be expected to match
        library = ConvertLibrary.lims_to_ngi(lims_model=lims_sample_obj)
        skip_attributes = [
            "description",
            "sample"
        ]
        assert type(library.sample) == type(ngi_library_obj.sample)
        for attr in set(
                list(
                    vars(
                        ngi_library_obj
                    ).keys()
                ) +
                list(
                    vars(
                        library
                    ).keys()
                )
        ):
            if attr not in skip_attributes:
                assert getattr(library, attr) == getattr(ngi_library_obj, attr)

    def test_objects_from_application_info(self, test_values):
        assert ConvertLibrary.objects_from_application_info(
            application=test_values["experiment_application"],
            sample_type=test_values["experiment_sample_type"],
            library_kit=test_values["experiment_library_kit"],
        ) == (
            test_values["experiment_library_selection_value"],
            test_values["experiment_sample_source"],
            test_values["experiment_library_strategy_value"],
        )


class TestConvertExperiment:
    def test_ngi_to_sra(self, ngi_experiment_obj, sra_experiment_obj):
        assert Converter.ngi_to_sra(ngi_model=ngi_experiment_obj) == sra_experiment_obj

    def test_lims_to_ngi(self, lims_sample_obj, ngi_experiment_obj):
        # the converted object will have a derived alias and title that don't correspond to the
        # fixture so compare only fields that can be expected to match
        experiment = ConvertExperiment.lims_to_ngi(lims_model=lims_sample_obj)
        assert type(experiment.library) is type(ngi_experiment_obj.library)
        assert type(experiment.platform) is type(ngi_experiment_obj.platform)
        assert type(experiment.project) is type(ngi_experiment_obj.project)
