import datetime

from snpseq_metadata.models.sra_models.sequencing_run import SRARun


class TestSRARun:
    def test_create_object(
        self,
        sra_sequencing_run_obj,
        sra_sequencing_run_json,
        sra_experiment_obj,
        sra_result_file_obj,
    ):
        sequencing_run = SRARun.create_object(
            run_alias=sra_sequencing_run_json["TITLE"],
            run_center=sra_sequencing_run_json["run_center"],
            run_date=datetime.datetime.fromisoformat(
                sra_sequencing_run_json["run_date"]
            ),
            experiment=sra_experiment_obj,
            fastqfiles=[sra_result_file_obj],
        )
        assert sequencing_run == sra_sequencing_run_obj

    def test_to_json(self, sra_sequencing_run_obj, sra_sequencing_run_json):
        assert sra_sequencing_run_obj.to_json() == sra_sequencing_run_json

    def test_to_manifest(self, sra_sequencing_run_obj, sra_sequencing_run_manifest):
        assert sra_sequencing_run_obj.to_manifest() == sra_sequencing_run_manifest

    def test_to_xml(self, sra_sequencing_run_obj, sra_sequencing_run_xml):
        assert "".join(sra_sequencing_run_xml.split()) in "".join(
            sra_sequencing_run_obj.to_xml().split()
        )

    def test_from_json(self, sra_sequencing_run_obj, sra_sequencing_run_json):
        sequencing_run = SRARun.from_json(json_obj=sra_sequencing_run_json)
        assert sequencing_run == sra_sequencing_run_obj.model_object
