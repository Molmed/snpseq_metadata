
from snpseq_metadata.models.sra_models.run_set import SRARun, SRARunSet

from tests.models.conftest import ignore_xml_namespace_attributes


class TestSRARunSet:
    def test_create_object(self, sra_sequencing_run_set_obj, sra_sequencing_run_obj):
        sequencing_run_set = SRARunSet.create_object(runs=[sra_sequencing_run_obj])
        assert sra_sequencing_run_set_obj == sequencing_run_set

    def test_from_json(self, sra_sequencing_run_set_obj, sra_sequencing_run_set_json):
        sequencing_run_set = SRARunSet.from_json(json_obj=sra_sequencing_run_set_json)
        assert sequencing_run_set == sra_sequencing_run_set_obj.model_object

    def test_to_json(self, sra_sequencing_run_set_obj, sra_sequencing_run_set_json):
        assert sra_sequencing_run_set_obj.to_json() == sra_sequencing_run_set_json

    def test_to_manifest(
        self, sra_sequencing_run_set_obj, sra_sequencing_run_set_manifest
    ):
        assert (
            sra_sequencing_run_set_obj.to_manifest() == sra_sequencing_run_set_manifest
        )

    def test_to_xml(self, sra_sequencing_run_set_obj, sra_sequencing_run_set_xml):
        observed_xml = ignore_xml_namespace_attributes(
            sra_sequencing_run_set_obj.to_xml(xml_declaration=False))
        assert "".join(observed_xml.split()) == "".join(
            sra_sequencing_run_set_xml.split()
        )

    @staticmethod
    def _create_run_with_attributes(
            sra_sequencing_run_json,
            sra_sequencing_run_obj,
            sra_study_obj,
            sra_sample_obj):
        # first, set the run attributes for project_id and sample_id on the run objects
        run_attributes = {
            "RUN_ATTRIBUTE": [
                {
                    "TAG": "project_id",
                    "VALUE": sra_study_obj.refname
                },
                {
                    "TAG": "sample_id",
                    "VALUE": sra_sample_obj.refname
                }
            ]
        }
        sra_sequencing_run_json["RUN_ATTRIBUTES"] = run_attributes
        run_model_object = SRARun.from_json(json_obj=sra_sequencing_run_json)
        run_obj = SRARun(model_object=run_model_object)
        return run_obj

    def test_restrict_to_experiments(
            self,
            sra_sequencing_run_json,
            sra_sequencing_run_obj,
            sra_study_obj,
            sra_sample_obj,
            sra_experiment_set_obj
    ):

        run_obj = self._create_run_with_attributes(
            sra_sequencing_run_json,
            sra_sequencing_run_obj,
            sra_study_obj,
            sra_sample_obj)
        sra_sequencing_run_set_obj = SRARunSet.create_object(runs=[run_obj])

        sequencing_run_set = sra_sequencing_run_set_obj.restrict_to_experiments(
            experiments=sra_experiment_set_obj
        )
        assert [
            run.experiment for run in sequencing_run_set.runs
        ] == sra_experiment_set_obj.experiments

    def test_get_sequencing_run_for_experiment(
            self,
            sra_sequencing_run_json,
            sra_sequencing_run_obj,
            sra_study_obj,
            sra_sample_obj,
            sra_experiment_obj):
        run_obj = self._create_run_with_attributes(
            sra_sequencing_run_json,
            sra_sequencing_run_obj,
            sra_study_obj,
            sra_sample_obj)
        sra_sequencing_run_set_obj = SRARunSet.create_object(runs=[run_obj])
        assert (
                sra_sequencing_run_set_obj.get_sequencing_run_for_experiment(
                    sra_experiment_obj) == run_obj)
