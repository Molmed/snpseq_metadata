
import csv
import json


class SnpseqDataSample:

    SNPSEQ_DATA_FIELDNAMES = [
        'name',
        'project',
        'udf_application',
        'udf_conc_fc',
        'udf_current_sample_volume_ul',
        'udf_custom_sequencing_primer',
        'udf_data_analysis',
        'udf_genotyping_idpanel',
        'udf_id',
        'udf_index',
        'udf_index2',
        'udf_insert_size_bp',
        'udf_library_preparation_kit',
        'udf_number_of_lanes',
        'udf_of_libraries_per_sample',
        'udf_phix_',
        'udf_plate_',
        'udf_pooling',
        'udf_progress',
        'udf_read_length',
        'udf_rml_kitprotocol',
        'udf_sample_conc',
        'udf_sample_type',
        'udf_seq_data_coverage_x',
        'udf_sequencing_instrument',
        'udf_special_info_prep',
        'udf_special_info_seq',
        'udf_species',
        'udf_volume_ul'
    ]

    EXPERIMENT_NGI_JSON_STRUCTURE = """
        {
          "alias": "{experiment_ngi_alias}",
          "project": {
            "project_id": "{experiment_ngi_project_id}"
          },
          "title": "{experiment_ngi_title}",
          "platform": {
            "model_name": "{experiment_ngi_model_name}"
          },
          "library": {
            "sample": {
              "sample_id": "{experiment_ngi_sample_id}"
            },
            "application": "{experiment_ngi_application}",
            "sample_type": "{experiment_ngi_sample_type}",
            "library_kit": "{experiment_ngi_library_kit}",
            "is_paired": {experiment_ngi_is_paired}
          }
        }
    """

    EXPERIMENT_SRA_JSON_STRUCTURE = """
        {
          "alias": "{experiment_sra_alias}",
          "TITLE": "{experiment_sra_title}",
          "STUDY_REF": {
            "refname": "{experiment_sra_study_refname}"
          },
          "DESIGN": {
            "SAMPLE_DESCRIPTOR": {
              "refname": "{experiment_sra_sample_refname}"
            },
            "LIBRARY_DESCRIPTOR": {
              "LIBRARY_STRATEGY": "{experiment_sra_library_strategy}",
              "LIBRARY_SOURCE": "{experiment_sra_library_source}",
              "LIBRARY_SELECTION": "{experiment_sra_library_selection}",
              "LIBRARY_LAYOUT": {
                "PAIRED": {}
              }
            }
          },
          "PLATFORM": {
            "{experiment_sra_platform}": {
              "INSTRUMENT_MODEL": "{experiment_sra_instrument_model}"
            }
          }
        }
    """

    EXPERIMENT_SRA_XML_STRUCTURE = """
        <EXPERIMENT alias="{experiment_sra_alias}">
        <TITLE>{experiment_sra_title}</TITLE>
        <STUDY_REF refname="{experiment_sra_study_refname}"/>
        <DESIGN>
          <SAMPLE_DESCRIPTOR refname="{experiment_sra_sample_refname}"/>
          <LIBRARY_DESCRIPTOR>
            <LIBRARY_STRATEGY>{experiment_sra_library_strategy}</LIBRARY_STRATEGY>
            <LIBRARY_SOURCE>{experiment_sra_library_source}</LIBRARY_SOURCE>
            <LIBRARY_SELECTION>{experiment_sra_library_selection}</LIBRARY_SELECTION>
            <LIBRARY_LAYOUT>
              <PAIRED/>
            </LIBRARY_LAYOUT>
          </LIBRARY_DESCRIPTOR>
        </DESIGN>
        <PLATFORM>
          <{experiment_sra_platform}>
            <INSTRUMENT_MODEL>{experiment_sra_instrument_model}</INSTRUMENT_MODEL>
          </{experiment_sra_platform}>
        </PLATFORM>
        </EXPERIMENT>
    """

    SAMPLE_SRA_MANIFEST = [
        ["NAME", "{experiment_sra_alias}"],
        ["STUDY", "{experiment_sra_study_refname}"],
        ["PLATFORM", "{experiment_sra_platform}"],
        ["INSTRUMENT", "{experiment_sra_instrument_model}"],
        ["LIBRARY_STRATEGY", "{experiment_sra_library_strategy}"],
        ["LIBRARY_SOURCE", "{experiment_sra_library_source}"],
        ["LIBRARY_SELECTION", "{experiment_sra_library_selection}"],
        ["SAMPLE", "{experiment_sra_sample_refname}"]
    ]

    def __init__(self, fields):
        self.fields = fields

    def flowcell_id(self):
        return self.fields.get("flowcell_id", "FCID")

    def snpseq_data_json(self):
        return {k: self.fields.get(k, "") for k in self.SNPSEQ_DATA_FIELDNAMES}

    def experiment_ngi_json(self):
        return json.loads(
            self.EXPERIMENT_NGI_JSON_STRUCTURE.format(**self.fields)
        )

    def experiment_sra_json(self):
        return json.loads(
            self.EXPERIMENT_SRA_JSON_STRUCTURE.format(**self.fields)
        )

    def experiment_sra_xml(self):
        return self.EXPERIMENT_SRA_XML_STRUCTURE.format(**self.fields)

    def sample_sra_manifest(self):
        return [
            self.fields.get("experiment_sra_sample_refname", ""),
            "\n".join(
                [
                    "\t".join(
                        [manifest[0], manifest[1].format(**self.fields)])
                    for manifest in self.SAMPLE_SRA_MANIFEST
                ]
            )
        ]

    @staticmethod
    def create_from_csv(csv_file):
        fields = dict()
        with open(csv_file) as fh:
            reader = csv.reader(fh, dialect=csv.excel_tab)
            for row in reader:
                fields[row[0]] = row[1]
        return SnpseqDataSample(fields=fields)


class SnpseqDataRun:

    SNPSEQDATA_RUN_JSON_STRUCTURE = {
        "result": {
            "name": "{flowcell_id}",
            "samples": []
        }
    }

    EXPERIMENTS_NGI_JSON_STRUCTURE = {
        "experiments": []
    }

    EXPERIMENTS_SRA_JSON_STRUCTURE = {
        "EXPERIMENT": []
    }

    EXPERIMENTS_SRA_XML_STRUCTURE = """
        <?xml version="1.0" encoding="UTF-8"?>
        <EXPERIMENT_SET>
            {experiment_sra_xml}
        </EXPERIMENT_SET>
    """

    def __init__(self, flowcell_id, samples):
        self.flowcell_id = flowcell_id
        self.samples = samples

    def snpseq_data_json(self):
        run_json = self.SNPSEQDATA_RUN_JSON_STRUCTURE.copy()
        run_json["result"]["name"].format(
            flowcell_id=self.flowcell_id)
        run_json["result"]["samples"] = [
            sample.snpseq_data_json()
            for sample in self.samples
        ]
        return run_json

    def experiments_ngi_json(self):
        experiments_json = self.EXPERIMENTS_NGI_JSON_STRUCTURE.copy()
        experiments_json["experiments"] = [
            sample.experiment_ngi_json()
            for sample in self.samples
        ]
        return experiments_json

    def experiments_sra_json(self):
        experiments_json = self.EXPERIMENTS_SRA_JSON_STRUCTURE.copy()
        experiments_json["EXPERIMENT"] = [
            sample.experiment_sra_json()
            for sample in self.samples
        ]
        return experiments_json

    def experiments_sra_xml(self):
        return self.EXPERIMENTS_SRA_XML_STRUCTURE.format(
            experiment_sra_xml="\n".join(
                [
                    sample.experiment_sra_xml()
                    for sample in self.samples
                ]
            )
        )

    def run_sra_manifest(self):
        manifests = dict()
        for sample in self.samples:
            m = sample.sample_sra_manifest()
            manifests[m[0]] = m[1]
        return manifests

    @staticmethod
    def create_from_sample_csv(csv_files):
        samples = [
            SnpseqDataSample.create_from_csv(csv_file) for csv_file in csv_files
        ]
        flowcell_id = samples[0].flowcell_id()
        return SnpseqDataRun(flowcell_id=flowcell_id, samples=samples)
